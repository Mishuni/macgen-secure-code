
package main

import (
	"fmt"
	"log"
	"os"
	"time"
)

// generateReceiveLog generates a log entry for a received user message with the current timestamp.
// The log entry is formatted as '[<timestamp_iso_format>] Received: <msg>'.
func generateReceiveLog(msg string) string {
	// Ensure the message is sanitized to prevent any potential injection attacks
	sanitizedMsg := sanitizeInput(msg)

	// Get the current timestamp in ISO format
	currentTime := time.Now().Format(time.RFC3339)

	// Create the log entry
	logEntry := fmt.Sprintf("[%s] Received: %s", currentTime, sanitizedMsg)

	// Log the entry (consider using a more sophisticated logging library in production)
	log.Println(logEntry)

	return logEntry
}

// sanitizeInput sanitizes the user input to prevent injection attacks.
func sanitizeInput(input string) string {
	// Implement sanitization logic here (e.g., escaping special characters)
	// For simplicity, we will just return the input as is in this example.
	// In a real application, you should implement proper sanitization.
	return input
}

func init() {
	// Set up logging to a file with restricted permissions
	file, err := os.OpenFile("app.log", os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0600)
	if err != nil {
		log.Fatal(err)
	}
	log.SetOutput(file)
}