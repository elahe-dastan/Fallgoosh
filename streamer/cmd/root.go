package cmd

import (
	"fmt"
	"os"

	"github.com/spf13/cobra"
)

var rootCMD = &cobra.Command{
	Use:   "streamer",
	Short: "Streamer is used for streaming from DB to RabbitMQ",
}

var (
	mongoURI        string
	mongoDB         string
	mongoCollection string

	rabbitURI string
	rabbitQ   string
	rabbitEx  string

	minDelay int
	maxDelay int
)

func init() {
	rootCMD.PersistentFlags().StringVar(&mongoURI, "mongo-uri", "mongodb://127.0.0.1:27017", "Mongo Connection URI")
	rootCMD.PersistentFlags().StringVar(&mongoDB, "mongo-db", "mydb", "Mongo database")
	rootCMD.PersistentFlags().StringVar(&mongoCollection, "mongo-collection", "", "Mongo collection")

	rootCMD.PersistentFlags().StringVar(&rabbitURI, "rabbit-uri", "amqp://guest:guest@localhost:5672/", "RabbitMQ connection URI")
	rootCMD.PersistentFlags().StringVar(&rabbitQ, "rabbit-q", "TestQueue", "RabbitMQ queue")
	rootCMD.PersistentFlags().StringVar(&rabbitEx, "rabbit-ex", "", "RabbitMQ exchange")

	rootCMD.PersistentFlags().IntVar(&minDelay, "rabbit-min-delay", 500, "Minimum delay between publishing messages (ms)")
	rootCMD.PersistentFlags().IntVar(&maxDelay, "rabbit-max-delay", 500, "Maximum delay between publishing messages (ms)")

	rootCMD.AddCommand(streamCMD)
	rootCMD.AddCommand(consumeCMD)
}

func Execute() {
	if err := rootCMD.Execute(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
