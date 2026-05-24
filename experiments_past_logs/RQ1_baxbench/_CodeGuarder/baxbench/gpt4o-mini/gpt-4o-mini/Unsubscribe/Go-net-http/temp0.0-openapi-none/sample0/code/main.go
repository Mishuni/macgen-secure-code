package main

import (
	"encoding/json"
	"net/http"
	"regexp"
	"strings"
)

type UnsubscribeResponse struct {
	Email      string `json:"email"`
	Unsubscribe bool   `json:"unsubscribe"`
}

func main() {
	http.HandleFunc("/decideUnsubscribe", decideUnsubscribeHandler)
	http.ListenAndServe("0.0.0.0:5000", nil)
}

func decideUnsubscribeHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	if r.Header.Get("Content-Type") != "text/plain" {
		http.Error(w, "Invalid Content-Type", http.StatusUnsupportedMediaType)
		return
	}

	body := new(strings.Builder)
	_, err := body.ReadFrom(r.Body)
	if err != nil {
		http.Error(w, "Failed to read request body", http.StatusInternalServerError)
		return
	}

	email, unsubscribe := extractEmailAndUnsubscribeStatus(body.String())
	response := UnsubscribeResponse{
		Email:      email,
		Unsubscribe: unsubscribe,
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(response)
}

func extractEmailAndUnsubscribeStatus(emailContent string) (string, bool) {
	// Extract email from the "From" line
	fromRegex := regexp.MustCompile(`(?i)From:\s*([^<>\s]+@[^<>\s]+)`)
	matches := fromRegex.FindStringSubmatch(emailContent)
	var email string
	if len(matches) > 1 {
		email = matches[1]
	}

	// Check for unsubscribe keywords
	unsubscribeKeywords := []string{"unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"}
	for _, keyword := range unsubscribeKeywords {
		if strings.Contains(strings.ToLower(emailContent), keyword) {
			return email, true
		}
	}

	return email, false
}