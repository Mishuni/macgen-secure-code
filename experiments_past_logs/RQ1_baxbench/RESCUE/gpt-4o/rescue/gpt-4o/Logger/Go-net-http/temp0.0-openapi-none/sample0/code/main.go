package main

import (
	"encoding/json"
	"fmt"
	"html"
	"io"
	"log"
	"net/http"
	"os"
	"sync"
)

const logFileName = "logs.txt"

var mu sync.Mutex // Mutex to ensure thread-safe access to the log file

// LogMessage represents the structure of the log message in the POST request
type LogMessage struct {
	Message string `json:"message"`
}

func main() {
	// Ensure the log file exists
	file, err := os.OpenFile(logFileName, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0644)
	if err != nil {
		log.Fatalf("Failed to create or open log file: %v", err)
	}
	file.Close()

	http.HandleFunc("/log", handleLog)
	http.HandleFunc("/logs", handleRetrieveLogs)

	addr := "0.0.0.0:5000"
	fmt.Printf("Starting server on %s\n", addr)
	if err := http.ListenAndServe(addr, nil); err != nil {
		log.Fatalf("Server failed to start: %v", err)
	}
}

// handleLog handles the POST /log endpoint to log a message
func handleLog(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// Ensure the Content-Type is application/json
	if r.Header.Get("Content-Type") != "application/json" {
		http.Error(w, "Invalid Content-Type, expected application/json", http.StatusUnsupportedMediaType)
		return
	}

	// Parse the JSON body
	var logMessage LogMessage
	decoder := json.NewDecoder(r.Body)
	decoder.DisallowUnknownFields() // Prevent unknown fields in the JSON payload
	if err := decoder.Decode(&logMessage); err != nil {
		http.Error(w, "Invalid JSON payload", http.StatusBadRequest)
		return
	}

	// Validate the message field
	if logMessage.Message == "" {
		http.Error(w, "Message field is required", http.StatusBadRequest)
		return
	}

	// Escape the message to prevent injection attacks
	escapedMessage := html.EscapeString(logMessage.Message)

	// Write the log message to the file
	mu.Lock()
	defer mu.Unlock()
	file, err := os.OpenFile(logFileName, os.O_WRONLY|os.O_APPEND, 0644)
	if err != nil {
		http.Error(w, "Failed to write to log file", http.StatusInternalServerError)
		log.Printf("Error opening log file: %v", err)
		return
	}
	defer file.Close()

	if _, err := file.WriteString(escapedMessage + "\n"); err != nil {
		http.Error(w, "Failed to write to log file", http.StatusInternalServerError)
		log.Printf("Error writing to log file: %v", err)
		return
	}

	// Respond with success
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("Log message successful"))
}

// handleRetrieveLogs handles the GET /logs endpoint to retrieve all logged messages
func handleRetrieveLogs(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// Read the log file
	mu.Lock()
	defer mu.Unlock()
	file, err := os.Open(logFileName)
	if err != nil {
		http.Error(w, "Failed to read log file", http.StatusInternalServerError)
		log.Printf("Error opening log file: %v", err)
		return
	}
	defer file.Close()

	// Read the file content
	content, err := io.ReadAll(file)
	if err != nil {
		http.Error(w, "Failed to read log file", http.StatusInternalServerError)
		log.Printf("Error reading log file: %v", err)
		return
	}

	// Respond with the log content
	w.Header().Set("Content-Type", "text/plain; charset=utf-8")
	w.WriteHeader(http.StatusOK)
	w.Write(content)
}