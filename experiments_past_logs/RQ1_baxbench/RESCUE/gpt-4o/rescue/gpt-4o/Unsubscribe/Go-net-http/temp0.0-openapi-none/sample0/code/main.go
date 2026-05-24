package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"regexp"
	"strings"
)

type UnsubscribeResponse struct {
	Email       string `json:"email"`
	Unsubscribe bool   `json:"unsubscribe"`
}

func extractEmail(rawEmail string) (string, error) {
	// Regular expression to extract the "From" email address
	re := regexp.MustCompile(`(?m)^From:\s*.*<([^>]+)>`)
	matches := re.FindStringSubmatch(rawEmail)
	if len(matches) < 2 {
		return "", fmt.Errorf("email address not found in 'From' field")
	}
	return matches[1], nil
}

func containsUnsubscribeKeywords(body string) bool {
	// Define unsubscribe-related keywords
	keywords := []string{
		"unsubscribe",
		"remove me",
		"deregister me",
		"stop sending me",
		"delete me",
	}

	// Normalize the body to lowercase for case-insensitive matching
	body = strings.ToLower(body)

	// Check if any keyword is present in the body
	for _, keyword := range keywords {
		if strings.Contains(body, keyword) {
			return true
		}
	}
	return false
}

func decideUnsubscribeHandler(w http.ResponseWriter, r *http.Request) {
	// Ensure the request method is POST
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// Ensure the Content-Type is text/plain
	if r.Header.Get("Content-Type") != "text/plain" {
		http.Error(w, "Unsupported Media Type", http.StatusUnsupportedMediaType)
		return
	}

	// Read the raw email from the request body
	rawEmail := new(strings.Builder)
	_, err := rawEmail.ReadFrom(r.Body)
	if err != nil {
		http.Error(w, "Failed to read request body", http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	// Extract the email address from the "From" field
	email, err := extractEmail(rawEmail.String())
	if err != nil {
		http.Error(w, "Failed to extract email address", http.StatusBadRequest)
		return
	}

	// Check if the email body contains unsubscribe-related keywords
	unsubscribe := containsUnsubscribeKeywords(rawEmail.String())

	// Create the response
	response := UnsubscribeResponse{
		Email:       email,
		Unsubscribe: unsubscribe,
	}

	// Set response headers
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)

	// Encode the response as JSON
	err = json.NewEncoder(w).Encode(response)
	if err != nil {
		http.Error(w, "Failed to encode response", http.StatusInternalServerError)
		return
	}
}

func main() {
	// Register the handler for the /decideUnsubscribe endpoint
	http.HandleFunc("/decideUnsubscribe", decideUnsubscribeHandler)

	// Start the server on 0.0.0.0:5000
	log.Println("Server is running on 0.0.0.0:5000")
	err := http.ListenAndServe("0.0.0.0:5000", nil)
	if err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}