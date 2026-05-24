
package main

import (
	"fmt"
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