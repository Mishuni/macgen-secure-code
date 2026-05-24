package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"strings"
)

type LogMessage struct {
	Message string `json:"message"`
}

func logHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var logMessage LogMessage
	err := json.NewDecoder(r.Body).Decode(&logMessage)
	if err != nil {
		http.Error(w, "Bad request", http.StatusBadRequest)
		return
	}

	if strings.ContainsAny(logMessage.Message, "\n\r") {
		http.Error(w, "Invalid log message", http.StatusBadRequest)
		return
	}

	file, err := os.OpenFile("logs.txt", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0600)
	if err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}
	defer func() {
		if err := file.Close(); err != nil {
			log.Println("Error closing file:", err)
		}
	}()

	if _, err := file.WriteString(logMessage.Message + "\n"); err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
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

	data, err := ioutil.ReadFile("logs.txt")
	if err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "text/plain")
	w.WriteHeader(http.StatusOK)
	w.Write(data)
}

func main() {
	http.HandleFunc("/log", logHandler)
	http.HandleFunc("/logs", logsHandler)

	http.ListenAndServe("0.0.0.0:5000", nil)
}