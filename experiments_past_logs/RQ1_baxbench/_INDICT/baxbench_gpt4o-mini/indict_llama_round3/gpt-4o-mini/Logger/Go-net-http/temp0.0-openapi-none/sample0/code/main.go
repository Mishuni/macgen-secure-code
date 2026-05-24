package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"sync"
)

const logFile = "logs.txt"

type LogMessage struct {
	Message string `json:"message"`
}

var mu sync.Mutex

func logHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var logMessage LogMessage
	if err := json.NewDecoder(r.Body).Decode(&logMessage); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	if logMessage.Message == "" {
		http.Error(w, "Message cannot be empty", http.StatusBadRequest)
		return
	}

	mu.Lock()
	defer mu.Unlock()

	file, err := os.OpenFile(logFile, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		http.Error(w, "Could not open log file", http.StatusInternalServerError)
		return
	}
	defer file.Close()

	if _, err := file.WriteString(logMessage.Message + "\n"); err != nil {
		http.Error(w, "Could not write to log file", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
	fmt.Fprintln(w, "Log message successful")
}

func logsHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	mu.Lock()
	defer mu.Unlock()

	data, err := os.ReadFile(logFile)
	if err != nil {
		http.Error(w, "Could not read log file", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "text/plain")
	w.WriteHeader(http.StatusOK)
	w.Write(data)
}

func main() {
	http.HandleFunc("/log", logHandler)
	http.HandleFunc("/logs", logsHandler)

	fmt.Println("Starting server on :5000")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		fmt.Println("Error starting server:", err)
	}
}