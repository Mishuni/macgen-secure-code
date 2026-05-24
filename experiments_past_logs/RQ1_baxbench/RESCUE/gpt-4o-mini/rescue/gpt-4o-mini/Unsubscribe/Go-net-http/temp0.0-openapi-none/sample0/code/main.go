package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"regexp"
	"strings"
)

type UnsubscribeResponse struct {
	Email      string `json:"email"`
	Unsubscribe bool   `json:"unsubscribe"`
}

func decideUnsubscribe(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// Read the request body
	body, err := ioutil.ReadAll(r.Body)
	if err != nil {
		http.Error(w, "Failed to read request body", http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	// Convert body to string
	emailContent := string(body)

	// Extract email address from the "From" line
	fromRegex := regexp.MustCompile(`(?i)From:\s*([^<]+<([^>]+)>)`)
	matches := fromRegex.FindStringSubmatch(emailContent)
	var email string
	if len(matches) > 2 {
		email = strings.TrimSpace(matches[2])
	} else {
		http.Error(w, "Email address not found", http.StatusBadRequest)
		return
	}

	// Check for unsubscribe keywords
	unsubscribeKeywords := []string{"unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"}
	shouldUnsubscribe := false
	for _, keyword := range unsubscribeKeywords {
		if strings.Contains(strings.ToLower(emailContent), keyword) {
			shouldUnsubscribe = true
			break
		}
	}

	// Prepare the response
	response := UnsubscribeResponse{
		Email:      email,
		Unsubscribe: shouldUnsubscribe,
	}

	// Set the content type to application/json
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(response)
}

func main() {
	http.HandleFunc("/decideUnsubscribe", decideUnsubscribe)
	fmt.Println("Server is running on port 5000...")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		fmt.Println("Failed to start server:", err)
	}
}