package cmd

import (
	"context"
	"encoding/json"
	"fmt"
	"math/rand"
	"time"

	log "github.com/sirupsen/logrus"
	"github.com/spf13/cobra"
	"github.com/streadway/amqp"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo/options"

	"github.com/elahe-dastan/Fallgoosh/streamer/database"
)

var (
	streamCMD = &cobra.Command{
		Use:   "stream",
		Short: "Start the streaming process",
		Run: func(cmd *cobra.Command, args []string) {
			stream()
		},
	}
)

func stream() {
	db, err := database.Connect(mongoURI)
	if err != nil {
		log.WithField("error", err).Fatal("error in connecting to db")
	}

	log.Info("Successfully connected to database")
	defer db.Disconnect(context.Background())

	collection := db.Database(mongoDB).Collection(mongoCollection)

	findOptions := options.Find()
	cur, err := collection.Find(context.TODO(), bson.D{{}}, findOptions)
	if err != nil {
		log.WithField("error", err).Fatal("error in finding in DB collection")
	}

	mq, err := amqp.Dial(rabbitURI)
	if err != nil {
		log.WithField("error", err).Fatal("error in dialing to rabbit")
	}
	defer mq.Close()

	log.Info("Successfully Connected to our RabbitMQ Instance")

	// Let's start by opening a channel to our RabbitMQ instance
	// over the connection we have already established
	ch, err := mq.Channel()
	if err != nil {
		log.WithField("error", err).Fatal("error in rabbit channel")
	}
	defer ch.Close()

	q, err := ch.QueueDeclare(
		rabbitQ,
		false,
		false,
		false,
		false,
		nil,
	)
	if err != nil {
		log.WithField("error", err).Fatal("error in declaring the queue")
	}

	log.WithField("message_count", q.Messages).Info("Successfully queue declared")
	done := make(chan bool)

	go func() {
		for {
			select {
			case <-done:
				return
			default:
				if cur.Next(context.TODO()) {
					var elem = make(map[string]interface{})
					err := cur.Decode(&elem)
					if err != nil {
						log.WithField("error", err).Error("error in cursor decoding")
					}

					m, err := json.Marshal(elem)
					if err != nil {
						log.WithField("error", err).Error("error in json marshaling")
					}

					// attempt to publish a message to the queue!
					err = ch.Publish(
						rabbitEx,
						rabbitQ,
						false,
						false,
						amqp.Publishing{
							ContentType: "text/plain",
							Body:        m,
						},
					)
					if err != nil {
						log.WithField("error", err).Error("error in publishing message")
					}

					log.WithField("m", string(m)).Info("Successfully Published Message to Queue")

					rand.Seed(time.Now().UnixNano())
					delay := rand.Intn(maxDelay-minDelay+1) + minDelay
					time.Sleep(time.Duration(int64(delay)) * time.Millisecond)
				} else {
					done <- true
				}
			}
		}
	}()
	<-done
	cur.Close(context.TODO())
	fmt.Println("Finished")
}
