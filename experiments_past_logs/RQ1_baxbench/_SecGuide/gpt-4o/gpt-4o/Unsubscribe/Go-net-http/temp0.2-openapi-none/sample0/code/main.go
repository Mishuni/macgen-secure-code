package main

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"regexp"
	"strings"
)

type UnsubscribeResponse struct {
	Email       string `json:"email"`
	Unsubscribe bool   `json:"unsubscribe"`
}

func decideUnsubscribe(w http.ResponseWriter, r *http.Request) {
	// Check HTTP method
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// Set content type to JSON
	w.Header().Set("Content-Type", "application/json")

	// Limit the size of the request body to prevent DoS
	r.Body = http.MaxBytesReader(w, r.Body, 1048576) // 1MB limit

	// Check Content-Type
	if r.Header.Get("Content-Type") != "application/json" {
		http.Error(w, "Content-Type must be application/json", http.StatusUnsupportedMediaType)
		return
	}

	// Read the raw email from the request body
	emailContent, err := io.ReadAll(r.Body)
	if err != nil {
		http.Error(w, "Unable to read request body", http.StatusBadRequest)
		return
	}

	// Validate and sanitize input
	if len(emailContent) == 0 {
		http.Error(w, "Empty request body", http.StatusBadRequest)
		return
	}

	// Extract the email address from the "From" header
	emailRegex := regexp.MustCompile(`(?m)^From:\s*.*<([^<>@\s]+@[^<>@\s]+\.[^<>@\s]+)>`)
	matches := emailRegex.FindStringSubmatch(string(emailContent))
	if len(matches) < 2 {
		http.Error(w, "Invalid email format", http.StatusBadRequest)
		return
	}
	emailAddress := matches[1]

	// Normalize the email content for keyword matching
	normalizedContent := strings.ToLower(strings.TrimSpace(string(emailContent)))

	// Check for unsubscribe keywords
	unsubscribeKeywords := []string{"unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"}
	shouldUnsubscribe := false
	for _, keyword := range unsubscribeKeywords {
		if strings.Contains(normalizedContent, keyword) {
			shouldUnsubscribe = true
			break
		}
	}

	// Create the response
	response := UnsubscribeResponse{
		Email:       emailAddress,
		Unsubscribe: shouldUnsubscribe,
	}

	// Encode the response as JSON
	if err := json.NewEncoder(w).Encode(response); err != nil {
		http.Error(w, "Unable to encode response", http.StatusInternalServerError)
		return
	}
}

func main() {
	http.HandleFunc("/decideUnsubscribe", decideUnsubscribe)
	fmt.Println("Server starting on port 5000...")
	log.Fatal(http.ListenAndServeTLS("0.0.0.0:5000", "server.crt", "server.key", nil))
}