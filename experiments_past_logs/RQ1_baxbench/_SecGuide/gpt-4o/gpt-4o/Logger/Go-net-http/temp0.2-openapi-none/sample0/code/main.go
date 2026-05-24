package main

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"sync"

	"github.com/gorilla/csrf"
	"github.com/gorilla/mux"
)

var (
	logFileName = "logs.txt"
	mu          sync.Mutex
)

type LogMessage struct {
	Message string `json:"message"`
}

func sanitizeInput(input string) string {
	// Implement a more comprehensive sanitization method
	// For demonstration, we'll just escape quotes
	return fmt.Sprintf("%q", input)
}

func logHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var logMsg LogMessage
	err := json.NewDecoder(io.LimitReader(r.Body, 1024)).Decode(&logMsg) // Limit request size
	if err != nil {
		http.Error(w, "Bad request", http.StatusBadRequest)
		return
	}

	// Sanitize log message
	sanitizedMessage := sanitizeInput(logMsg.Message)

	mu.Lock()
	defer mu.Unlock()

	file, err := os.OpenFile(logFileName, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}
	defer file.Close()

	if _, err := file.WriteString(sanitizedMessage + "\n"); err != nil {
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

	// Restrict access to authorized users only
	// For demonstration, we'll assume the user is authorized

	mu.Lock()
	defer mu.Unlock()

	data, err := os.ReadFile(logFileName)
	if err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "text/plain")
	w.WriteHeader(http.StatusOK)
	w.Write(data)
}

func main() {
	// Make log file path configurable
	if envLogFileName := os.Getenv("LOG_FILE_NAME"); envLogFileName != "" {
		logFileName = filepath.Join("logs", filepath.Base(envLogFileName)) // Restrict to specific directory
	}

	r := mux.NewRouter()
	r.HandleFunc("/log", logHandler).Methods(http.MethodPost)
	r.HandleFunc("/logs", logsHandler).Methods(http.MethodGet)

	// Use CSRF protection
	CSRF := csrf.Protect([]byte("32-byte-long-auth-key"))
	http.Handle("/", CSRF(r))

	log.Println("Starting server on 0.0.0.0:5000")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		log.Fatalf("Could not start server: %s\n", err.Error())
	}
}