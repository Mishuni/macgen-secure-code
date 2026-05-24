package main

import (
	"fmt"
	"time"
)

func generateReceiveLog(msg string) string {
	currentTime := time.Now()
	timestamp := currentTime.Format(time.RFC3339)
	logEntry := fmt.Sprintf("[%s] Received: %s", timestamp, msg)
	return logEntry
}