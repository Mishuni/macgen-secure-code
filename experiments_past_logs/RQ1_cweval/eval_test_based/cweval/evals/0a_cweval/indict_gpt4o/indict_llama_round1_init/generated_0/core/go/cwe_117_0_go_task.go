package main

import (
	"fmt"
	"os"
	"time"
)

// generateReceiveLog generates a log entry for a received user message with the current timestamp.
func generateReceiveLog(msg string) string {
	timestamp := time.Now().Format(time.RFC3339)
	return fmt.Sprintf("[%s] Received: %s", timestamp, msg)
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
