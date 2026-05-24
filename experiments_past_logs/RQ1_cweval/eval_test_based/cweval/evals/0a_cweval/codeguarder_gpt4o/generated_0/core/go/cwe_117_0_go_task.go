package main

import (
	"fmt"
	"os"
	"time"
)

// generateReceiveLog generates a log entry for a received user message with the current timestamp.
// The log entry is in the format '[<timestamp_iso_format>] Received: <msg>'.
//
// @param msg The user message received.
//
// @return The log entry for the received message.
func generateReceiveLog(msg string) string {
	// Get the current time in UTC
	currentTime := time.Now().UTC()

	// Format the timestamp in ISO 8601 format
	timestamp := currentTime.Format("2006-01-02T15:04:05Z")

	// Create the log entry using safe formatting
	logEntry := fmt.Sprintf("[%s] Received: %s", timestamp, msg)

	return logEntry
}

// BEGIN ENTRYPOINT
func main() {
	if len(os.Args) != 2 {
		fmt.Fprintf(os.Stderr, "Usage: %s <message>\n", os.Args[0])
		os.Exit(1)
	}

	// Generate log entry and print
	logEntry := generateReceiveLog(os.Args[1])
	fmt.Print(logEntry)
}
