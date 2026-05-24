package main

import (
	"fmt"
	"os"
	"strings"
	"time"
)

func generateReceiveLog(msg string) string {
	// Sanitize input to prevent log injection
	msg = strings.ReplaceAll(msg, "\n", "\\n")
	msg = strings.ReplaceAll(msg, "[", "\\[")
	msg = strings.ReplaceAll(msg, "]", "\\]")

	// Get current time and format it to ISO 8601
	currentTime := time.Now()
	timestamp := currentTime.Format(time.RFC3339)

	// Construct the log entry
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
