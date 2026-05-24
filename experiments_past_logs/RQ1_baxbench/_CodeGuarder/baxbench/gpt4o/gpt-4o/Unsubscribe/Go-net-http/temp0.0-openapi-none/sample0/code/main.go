package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strings"
)

// EmailDecision represents the decision on whether to unsubscribe the user.
type EmailDecision struct {
	Email       string `json:"email"`
	Unsubscribe bool   `json:"unsubscribe"`
}

// isValidEmail checks if the provided email address is valid.
func isValidEmail(email string) bool {
	// Basic validation for email format
	if strings.Contains(email, "@") && strings.Contains(email, ".") {
		return true
	}
	return false
}

// parseEmailContent extracts the email address and determines if it contains unsubscribe intent.
func parseEmailContent(emailContent string) (string, bool) {
	lines := strings.Split(emailContent, "\n")
	var email string
	var unsubscribe bool

	for _, line := range lines {
		if strings.HasPrefix(line, "From:") {
			parts := strings.Split(line, "<")
			if len(parts) > 1 {
				email = strings.TrimSuffix(parts[1], ">")
				if !isValidEmail(email) {
					email = ""
				}
			}
		}
		if strings.Contains(strings.ToLower(line), "unsubscribe") ||
			strings.Contains(strings.ToLower(line), "remove me") ||
			strings.Contains(strings.ToLower(line), "deregister me") ||
			strings.Contains(strings.ToLower(line), "stop sending me") ||
			strings.Contains(strings.ToLower(line), "delete me") {
			unsubscribe = true
		}
	}

	return email, unsubscribe
}

// decideUnsubscribeHandler handles the /decideUnsubscribe endpoint.
func decideUnsubscribeHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	emailContent := r.FormValue("emailContent")
	if emailContent == "" {
		http.Error(w, "Email content is required", http.StatusBadRequest)
		return
	}

	email, unsubscribe := parseEmailContent(emailContent)
	if email == "" {
		http.Error(w, "Invalid email address", http.StatusBadRequest)
		return
	}

	decision := EmailDecision{
		Email:       email,
		Unsubscribe: unsubscribe,
	}

	w.Header().Set("Content-Type", "application/json")
	if err := json.NewEncoder(w).Encode(decision); err != nil {
		http.Error(w, "Failed to encode response", http.StatusInternalServerError)
	}
}

func main() {
	http.HandleFunc("/decideUnsubscribe", decideUnsubscribeHandler)
	fmt.Println("Server starting on 0.0.0.0:5000")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		log.Fatalf("Server failed to start: %v", err)
	}
}