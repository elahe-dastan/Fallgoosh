package cmd

import (
	"fmt"

	log "github.com/sirupsen/logrus"
	"github.com/spf13/cobra"
	"github.com/streadway/amqp"
)

var (
	consumeCMD = &cobra.Command{
		Use:   "consume",
		Short: "Start the consuming messages",
		Run: func(cmd *cobra.Command, args []string) {
			consume()
		},
	}
)

func consume() {
	conn, err := amqp.Dial(rabbitURI)
	if err != nil {
		log.WithField("error", err).Fatal("failed to connect to rabbitmq")
	}

	ch, err := conn.Channel()
	if err != nil {
		log.WithField("error", err).Fatal("failed to create channel")
	}
	defer ch.Close()

	msgs, err := ch.Consume(
		rabbitQ,
		rabbitEx,
		true,
		false,
		false,
		false,
		nil,
	)

	done := make(chan bool)
	go func() {
		for {
			select {
			case msg := <-msgs:
				log.WithField("msg", string(msg.Body)).Info("received Message")
			case <-done:
				break
			}
		}
	}()

	fmt.Println("Successfully Connected to our RabbitMQ Instance")
	fmt.Println(" [*] - Waiting for messages")
	<-done
}
