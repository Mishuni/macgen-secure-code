package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"regexp"
	"sync"
)

var (
	logFile = "logs.txt"
	mu      sync.Mutex
)

// LogMessage represents the structure of a log message
type LogMessage struct {
	Message string `json:"message"`
}

// sanitizeInput ensures that the log message is safe to write to the log file
func sanitizeInput(input string) string {
	// Remove newlines and control characters, and limit length
	re := regexp.MustCompile(`[^\x20-\x7E]+`) // Allow only printable ASCII characters
	sanitized := re.ReplaceAllString(input, "")
	if len(sanitized) > 256 { // Limit the length of the log message
		sanitized = sanitized[:256]
	}
	return sanitized
}

func logMessageHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var logMsg LogMessage
	if err := json.NewDecoder(r.Body).Decode(&logMsg); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	// Sanitize the log message
	logMsg.Message = sanitizeInput(logMsg.Message)

	mu.Lock()
	defer mu.Unlock()

	file, err := os.OpenFile(logFile, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0600) // Set stricter permissions
	if err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}
	defer file.Close()

	if _, err := file.WriteString(logMsg.Message + "\n"); err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
	fmt.Fprintln(w, "Log message successful")
}

func retrieveLogsHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	mu.Lock()
	defer mu.Unlock()

	data, err := os.ReadFile(logFile) // Use os.ReadFile instead of ioutil
	if err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "text/plain")
	w.WriteHeader(http.StatusOK)
	w.Write(data)
}

func main() {
	http.HandleFunc("/log", logMessageHandler)
	http.HandleFunc("/logs", retrieveLogsHandler)

	fmt.Println("Starting server on :5000")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		fmt.Println("Failed to start server:", err)
	}
}