
package main

import (
	"fmt"
	"time"
	"html"
)

/*
Generate a log entry for a received user message with the current timestamp, in the format '[<timestamp_iso_format>] Received: <msg>'.

@param msg The user message received.

@return The log entry for the received message.
*/
func generateReceiveLog(msg string) string {
	// Sanitize the user message to prevent XSS vulnerabilities
	sanitizedMsg := html.EscapeString(msg)

	// Get the current timestamp in ISO format
	currentTime := time.Now().Format(time.RFC3339)

	// Create the log entry
	logEntry := fmt.Sprintf("[%s] Received: %s", currentTime, sanitizedMsg)

	return logEntry
}