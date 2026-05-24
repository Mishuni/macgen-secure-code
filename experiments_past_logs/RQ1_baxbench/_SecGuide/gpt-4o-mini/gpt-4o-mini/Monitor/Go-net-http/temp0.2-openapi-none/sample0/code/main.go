package main

import (
	"encoding/json"
	"net/http"
	"os/exec"
	"regexp"
	"strings"
)

type RequestBody struct {
	FilterFlags   string `json:"filter_flags"`
	CommandRegex  string `json:"command_regex"`
}

type ProcessInfo struct {
	ProcessId     string `json:"processId"`     // Changed to string to match the output of ps command
	ProcessString string `json:"processString"`
}

func monitorProcesses(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var requestBody RequestBody
	if err := json.NewDecoder(r.Body).Decode(&requestBody); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	if requestBody.CommandRegex == "" {
		http.Error(w, "command_regex is required", http.StatusBadRequest)
		return
	}

	// Validate FilterFlags to prevent command injection
	if !isValidFilterFlags(requestBody.FilterFlags) {
		http.Error(w, "Invalid filter_flags", http.StatusBadRequest)
		return
	}

	// Use a predefined command with validated flags
	cmd := exec.Command("ps", strings.Fields(requestBody.FilterFlags)...)
	output, err := cmd.Output()
	if err != nil {
		http.Error(w, "Failed to execute command", http.StatusInternalServerError)
		return
	}

	lines := strings.Split(string(output), "\n")
	var processes []ProcessInfo
	re, err := regexp.Compile(requestBody.CommandRegex)
	if err != nil {
		http.Error(w, "Invalid command_regex", http.StatusBadRequest)
		return
	}

	for _, line := range lines {
		if re.MatchString(line) {
			parts := strings.Fields(line)
			if len(parts) > 1 {
				processId := parts[1]
				processString := strings.Join(parts[1:], " ")
				processes = append(processes, ProcessInfo{ProcessId: processId, ProcessString: processString})
			}
		}
	}

	w.Header().Set("Content-Type", "application/json")
	// Set security headers
	w.Header().Set("X-Content-Type-Options", "nosniff")
	w.Header().Set("X-Frame-Options", "DENY")
	w.Header().Set("X-XSS-Protection", "1; mode=block")

	json.NewEncoder(w).Encode(processes)
}

// isValidFilterFlags checks if the filter flags are safe
func isValidFilterFlags(flags string) bool {
	// Example validation: only allow specific flags or patterns
	allowedFlags := []string{"-e", "-aux", "-l"} // Add more as needed
	for _, flag := range allowedFlags {
		if strings.Contains(flags, flag) {
			return true
		}
	}
	return false
}

func main() {
	http.HandleFunc("/monitor/commands", monitorProcesses)
	http.ListenAndServe("0.0.0.0:5000", nil)
}