package main

import (
	"encoding/json"
	"io"
	"net/http"
	"regexp"
	"strings"
)

type Response struct {
	Email       string `json:"email"`
	Unsubscribe bool   `json:"unsubscribe"`
}

func decideUnsubscribe(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// Read the raw email from the request body
	emailContent, err := io.ReadAll(r.Body)
	if err != nil {
		http.Error(w, "Failed to read request body", http.StatusBadRequest)
		return
	}

	// Extract the "From" email address using regex
	fromRegex := regexp.MustCompile(`(?m)^From:\s*(?:.*?)(?:<(.+?)>)?\s*$`)
	fromMatches := fromRegex.FindStringSubmatch(string(emailContent))
	if len(fromMatches) < 2 {
		http.Error(w, "Invalid email format", http.StatusBadRequest)
		return
	}

	fromEmail := strings.TrimSpace(fromMatches[1])

	// Check for unsubscribe keywords
	unsubscribeKeywords := []string{"unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"}
	unsubscribe := false
	lowerContent := strings.ToLower(string(emailContent))
	for _, keyword := range unsubscribeKeywords {
		if strings.Contains(lowerContent, keyword) {
			unsubscribe = true
			break
		}
	}

	// Prepare the response
	response := Response{
		Email:       fromEmail,
		Unsubscribe: unsubscribe,
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(response)
}

func main() {
	http.HandleFunc("/decideUnsubscribe", decideUnsubscribe)
	http.ListenAndServe("0.0.0.0:5000", nil)
}