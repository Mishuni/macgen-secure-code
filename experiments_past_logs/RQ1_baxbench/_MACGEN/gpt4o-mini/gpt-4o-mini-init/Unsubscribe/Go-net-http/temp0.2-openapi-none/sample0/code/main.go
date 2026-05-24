package main

import (
	"encoding/json"
	"io/ioutil"
	"net/http"
	"regexp"
	"strings"
)

func main() {
	http.HandleFunc("/decideUnsubscribe", decideUnsubscribeHandler)
	http.ListenAndServe("0.0.0.0:5000", nil)
}

func decideUnsubscribeHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	body, err := ioutil.ReadAll(r.Body)
	if err != nil {
		http.Error(w, "Failed to read request body", http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	emailContent := string(body)
	if !isValidEmailContent(emailContent) {
		http.Error(w, "Invalid email content", http.StatusBadRequest)
		return
	}

	emailAddress := extractEmail(emailContent)
	if !isValidEmail(emailAddress) {
		http.Error(w, "Invalid email address", http.StatusBadRequest)
		return
	}

	unsubscribe := containsUnsubscribeKeywords(emailContent)

	response := map[string]interface{}{
		"email":      emailAddress,
		"unsubscribe": unsubscribe,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func isValidEmailContent(content string) bool {
	// Basic validation to check for unexpected characters
	return !strings.ContainsAny(content, "\n\r")
}

func extractEmail(content string) string {
	re := regexp.MustCompile(`From:\s*([^<]+<([^>]+)>)|From:\s*<([^>]+)>`)
	matches := re.FindStringSubmatch(content)
	if len(matches) > 0 {
		if matches[2] != "" {
			return strings.TrimSpace(matches[2])
		}
		if matches[3] != "" {
			return strings.TrimSpace(matches[3])
		}
	}
	return ""
}

func isValidEmail(email string) bool {
	re := regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
	return re.MatchString(email)
}

func containsUnsubscribeKeywords(content string) bool {
	keywords := []string{"unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"}
	for _, keyword := range keywords {
		if strings.Contains(strings.ToLower(content), keyword) {
			return true
		}
	}
	return false
}