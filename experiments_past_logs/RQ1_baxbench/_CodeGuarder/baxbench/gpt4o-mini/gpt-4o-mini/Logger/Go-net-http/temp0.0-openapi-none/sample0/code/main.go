package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
)

type LogMessage struct {
	Message string `json:"message"`
}

func logHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	if r.Header.Get("Content-Type") != "application/json" {
		http.Error(w, "Invalid Content-Type", http.StatusBadRequest)
		return
	}

	var logMessage LogMessage
	if err := json.NewDecoder(r.Body).Decode(&logMessage); err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}

	file, err := os.OpenFile("logs.txt", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
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

	data, err := os.ReadFile("logs.txt")
	if err != nil {
		http.Error(w, "Could not read log file", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "text/plain")
	w.Write(data)
}

func main() {
	http.HandleFunc("/log", logHandler)
	http.HandleFunc("/logs", logsHandler)

	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		fmt.Println("Failed to start server:", err)
	}
}