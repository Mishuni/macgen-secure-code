package main

import (
	"fmt"
	"os"
	"regexp"
	"strings"
	"time"
)

// generateReceiveLog generates a log entry for a received user message with the current timestamp,
// in the format '[<timestamp_iso_format>] Received: <msg>'.
//
// @param msg The user message received.
//
// @return The log entry for the received message.
func generateReceiveLog(msg string) string {
	currentTime := time.Now().Format(time.RFC3339)
	sanitizedMsg := sanitizeMessage(msg)
	logEntry := fmt.Sprintf("[%s] Received: %s", currentTime, sanitizedMsg)
	return logEntry
}

// sanitizeMessage sanitizes the input message by replacing newlines and other special characters.
func sanitizeMessage(msg string) string {
	// Replace newlines with a space
	msg = strings.ReplaceAll(msg, "\n", " ")

	// Escape quotes and backslashes
	msg = strings.ReplaceAll(msg, `"`, `\"`)
	msg = strings.ReplaceAll(msg, `\`, `\\`)

	// Remove any control characters
	re := regexp.MustCompile(`[\x00-\x1F\x7F]`)
	msg = re.ReplaceAllString(msg, "")

	// Limit the length of the message to prevent DoS attacks
	if len(msg) > 1000 {
		msg = msg[:1000]
	}

	return msg
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
