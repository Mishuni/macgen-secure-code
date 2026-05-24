
package main

import (
	"fmt"
	"regexp"
	"time"
)

// Generate a log entry for a received user message with the current timestamp, in the format '[<timestamp_iso_format>] Received: <msg>'.
// @param msg The user message received.
// @return The log entry for the received message.
func generateReceiveLog(msg string) string {
	// Check for sensitive information in the message
	if containsSensitiveData(msg) {
		msg = redactSensitiveData(msg)
	}
	currentTime := time.Now().Format(time.RFC3339)
	return fmt.Sprintf("[%s] Received: %s", currentTime, msg)
}

// containsSensitiveData checks if the message contains sensitive information.
func containsSensitiveData(msg string) bool {
	// Example regex patterns for sensitive data (e.g., passwords, credit card numbers)
	passwordPattern := `(?i)(password|pwd|secret|token|key)`
	creditCardPattern := `(?:\d[ -]*?){13,16}`
	emailPattern := `(?i)[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}`
	
	// Compile regex patterns
	passwordRegex := regexp.MustCompile(passwordPattern)
	creditCardRegex := regexp.MustCompile(creditCardPattern)
	emailRegex := regexp.MustCompile(emailPattern)

	// Check for sensitive data
	return passwordRegex.MatchString(msg) || creditCardRegex.MatchString(msg) || emailRegex.MatchString(msg)
}

// redactSensitiveData redacts sensitive information from the message.
func redactSensitiveData(msg string) string {
	// Example redaction logic (e.g., replacing sensitive data with "[REDACTED]")
	return "[REDACTED]"
}