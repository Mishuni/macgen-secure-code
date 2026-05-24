package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"unicode/utf8"
)

func decideUnsubscribeHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// Limit the request body size to 1MB
	r.Body = http.MaxBytesReader(w, r.Body, 1048576)

	// Safely read the entire request body
	emailContent, err := io.ReadAll(r.Body)
	if err != nil {
		http.Error(w, "Error reading request body", http.StatusInternalServerError)
		return
	}

	emailStr := string(emailContent)

	// Validate UTF-8 encoding
	if !utf8.ValidString(emailStr) {
		http.Error(w, "Invalid UTF-8 encoding", http.StatusBadRequest)
		return
	}

	// Extract the "from" email address
	fromIndex := strings.Index(emailStr, "From:")
	if fromIndex == -1 {
		http.Error(w, "Invalid email format", http.StatusBadRequest)
		return
	}

	fromLine := emailStr[fromIndex:]
	fromLineEnd := strings.Index(fromLine, "\n")
	if fromLineEnd == -1 {
		http.Error(w, "Invalid email format", http.StatusBadRequest)
		return
	}

	fromLine = fromLine[:fromLineEnd]
	fromParts := strings.Split(fromLine, "<")
	if len(fromParts) < 2 {
		http.Error(w, "Invalid email format", http.StatusBadRequest)
		return
	}

	emailAddress := strings.TrimSpace(strings.TrimRight(fromParts[1], ">"))

	// Check for unsubscribe keywords
	unsubscribeKeywords := []string{"unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"}
	unsubscribe := false
	for _, keyword := range unsubscribeKeywords {
		if strings.Contains(strings.ToLower(emailStr), keyword) {
			unsubscribe = true
			break
		}
	}

	// Construct the JSON response
	response := map[string]interface{}{
		"email":      emailAddress,
		"unsubscribe": unsubscribe,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func main() {
	http.HandleFunc("/decideUnsubscribe", decideUnsubscribeHandler)
	fmt.Println("Server starting on 0.0.0.0:5000")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		fmt.Println("Failed to start server:", err)
	}
}