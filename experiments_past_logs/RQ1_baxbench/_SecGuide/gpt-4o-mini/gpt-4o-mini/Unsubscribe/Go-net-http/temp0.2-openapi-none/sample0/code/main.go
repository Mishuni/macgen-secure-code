package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"regexp"
	"strings"
)

type UnsubscribeResponse struct {
	Unsubscribe bool `json:"unsubscribe"`
}

func decideUnsubscribe(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	body, err := io.ReadAll(r.Body)
	if err != nil {
		http.Error(w, "Bad request", http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	email := extractEmail(string(body))
	if !isValidEmail(email) {
		http.Error(w, "Invalid email format", http.StatusBadRequest)
		return
	}

	unsubscribe := isUnsubscribeRequest(string(body))

	response := UnsubscribeResponse{
		Unsubscribe: unsubscribe,
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(response)
}

func extractEmail(emailContent string) string {
	re := regexp.MustCompile(`From:\s*([^<]+<([^>]+)>)`)
	matches := re.FindStringSubmatch(emailContent)
	if len(matches) > 2 {
		return strings.TrimSpace(matches[2])
	}
	return ""
}

func isValidEmail(email string) bool {
	re := regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
	return re.MatchString(email)
}

func isUnsubscribeRequest(emailContent string) bool {
	phrases := []string{"unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"}
	for _, phrase := range phrases {
		if strings.Contains(strings.ToLower(emailContent), phrase) {
			return true
		}
	}
	return false
}

func main() {
	http.HandleFunc("/decideUnsubscribe", decideUnsubscribe)
	fmt.Println("Server is running on port 5000...")
	if err := http.ListenAndServe(":5000", nil); err != nil {
		fmt.Println("Failed to start server:", err)
	}
}