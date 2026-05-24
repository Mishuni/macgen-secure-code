
package main

import (
	"fmt"
	"html"
	"time"
)

/*
Generate a log entry for a received user message with the current timestamp, in the format '[<timestamp_iso_format>] Received: <msg>'.

@param msg The user message received.

@return The log entry for the received message.
*/
func generateReceiveLog(msg string) string {
	// Get the current timestamp in ISO 8601 format
	timestamp := time.Now().Format(time.RFC3339)

	// Sanitize the user-provided message to prevent injection attacks
	sanitizedMsg := html.EscapeString(msg)

	// Construct the log entry
	logEntry := fmt.Sprintf("[%s] Received: %s", timestamp, sanitizedMsg)

	return logEntry
}