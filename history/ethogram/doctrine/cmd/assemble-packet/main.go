package main

import (
	"os"

	"books.local/doctrine/internal/packet"
)

var retrieverVersion = "retriever-go-dev"

func main() {
	os.Exit(packet.Run(os.Args[1:], retrieverVersion, os.Stdout, os.Stderr))
}
