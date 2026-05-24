
package main

import (
	"time"
	"fmt"
)

// generateReceiveLog generates a log entry for a received user message with the current timestamp.
func generateReceiveLog(msg string) string {
	timestamp := time.Now().Format(time.RFC3339)
	return fmt.Sprintf("[%s] Received: %s", timestamp, msg)
}