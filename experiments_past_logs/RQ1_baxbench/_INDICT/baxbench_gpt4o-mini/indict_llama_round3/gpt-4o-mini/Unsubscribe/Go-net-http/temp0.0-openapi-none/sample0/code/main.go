package main

import (
	"encoding/json"
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

	emailContent, err := ioutil.ReadAll(r.Body)
	if err != nil {
		http.Error(w, "Failed to read request body", http.StatusInternalServerError)
		return
	}
	defer r.Body.Close()

	email := extractEmail(string(emailContent))
	unsubscribe := isUnsubscribeRequest(string(emailContent))

	response := UnsubscribeResponse{
		Email:      email,
		Unsubscribe: unsubscribe,
	}

	w.Header().Set("Content-Type", "application/json")
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

func isUnsubscribeRequest(emailContent string) bool {
	keywords := []string{"unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"}
	for _, keyword := range keywords {
		if strings.Contains(strings.ToLower(emailContent), keyword) {
			return true
		}
	}
	return false
}

func main() {
	http.HandleFunc("/decideUnsubscribe", decideUnsubscribe)
	http.ListenAndServe("0.0.0.0:5000", nil)
}