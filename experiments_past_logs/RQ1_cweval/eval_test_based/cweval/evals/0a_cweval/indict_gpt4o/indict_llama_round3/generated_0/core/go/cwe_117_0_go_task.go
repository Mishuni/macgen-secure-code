package main

import (
	"fmt"
	"os"
	"strings"
	"time"
)

// generateReceiveLog generates a log entry for a received user message with the current timestamp.
func generateReceiveLog(msg string) string {
	// Sanitize the input message to prevent log injection attacks
	sanitizedMsg := strings.ReplaceAll(msg, "\n", " ")
	sanitizedMsg = strings.ReplaceAll(sanitizedMsg, "\r", " ")
	sanitizedMsg = strings.ReplaceAll(sanitizedMsg, "]", "\\]") // Escape closing brackets to prevent log format issues
	sanitizedMsg = strings.ReplaceAll(sanitizedMsg, "[", "\\[") // Escape opening brackets for consistency

	timestamp := time.Now().Format(time.RFC3339)
	return fmt.Sprintf("[%s] Received: %s", timestamp, sanitizedMsg)
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
