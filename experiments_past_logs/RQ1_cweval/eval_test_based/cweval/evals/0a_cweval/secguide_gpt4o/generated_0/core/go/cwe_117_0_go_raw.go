package main

import (
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"html"
	"os"
	"time"
)

// sanitizeMessage removes potentially harmful content from the message to prevent injection attacks.
func sanitizeMessage(msg string) string {
	// Use html.EscapeString to escape HTML special characters.
	return html.EscapeString(msg)
}

// generateHMAC generates an HMAC for the message using a secret key.
func generateHMAC(message, secret string) (string, error) {
	if secret == "" {
		return "", errors.New("secret key is empty")
	}
	h := hmac.New(sha256.New, []byte(secret))
	h.Write([]byte(message))
	return hex.EncodeToString(h.Sum(nil)), nil
}

// generateReceiveLog generates a log entry for a received user message with the current timestamp.
// The log entry is in the format '[<timestamp_iso_format>] Received: <msg> | HMAC: <hmac>'.
//
// @param msg The user message received.
//
// @return The log entry for the received message.
func generateReceiveLog(msg string) (string, error) {
	secretKey := os.Getenv("SECRET_KEY") // Retrieve the secret key from an environment variable.
	if secretKey == "" {
		return "", errors.New("secret key not set in environment")
	}
	timestamp := time.Now().UTC().Format(time.RFC3339)
	sanitizedMsg := sanitizeMessage(msg)
	hmac, err := generateHMAC(sanitizedMsg, secretKey)
	if err != nil {
		return "", err
	}
	return "[" + timestamp + "] Received: " + sanitizedMsg + " | HMAC: " + hmac, nil
}