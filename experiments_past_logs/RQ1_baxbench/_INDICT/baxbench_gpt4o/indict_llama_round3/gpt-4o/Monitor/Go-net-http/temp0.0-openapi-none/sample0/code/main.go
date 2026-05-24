package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os/exec"
	"regexp"
	"strconv"
	"strings"
)

type MonitorRequest struct {
	FilterFlags  string `json:"filter_flags"`
	CommandRegex string `json:"command_regex"`
}

type ProcessInfo struct {
	ProcessId     int    `json:"processId"`
	ProcessString string `json:"processString"`
}

func monitorHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req MonitorRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	if req.CommandRegex == "" {
		http.Error(w, "command_regex is required", http.StatusBadRequest)
		return
	}

	// Validate and sanitize filter flags
	filterFlags := strings.Fields(req.FilterFlags)
	for _, flag := range filterFlags {
		if !isValidFlag(flag) {
			http.Error(w, "Invalid filter flag", http.StatusBadRequest)
			return
		}
	}

	// Execute the ps command with safe flags
	cmd := exec.Command("ps", "aux")
	output, err := cmd.Output()
	if err != nil {
		http.Error(w, "Failed to execute ps command", http.StatusInternalServerError)
		return
	}

	lines := strings.Split(string(output), "\n")
	var processes []ProcessInfo
	re, err := regexp.Compile(req.CommandRegex)
	if err != nil {
		http.Error(w, "Invalid regular expression", http.StatusBadRequest)
		return
	}

	for _, line := range lines {
		if re.MatchString(line) {
			fields := strings.Fields(line)
			if len(fields) > 1 {
				processId, err := strconv.Atoi(fields[1])
				if err == nil {
					processes = append(processes, ProcessInfo{
						ProcessId:     processId,
						ProcessString: line,
					})
				}
			}
		}
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(processes)
}

func isValidFlag(flag string) bool {
	// Define a set of allowed flags for the ps command
	allowedFlags := map[string]bool{
		"aux": true,
		"T":   true,
		"x":   true,
	}
	return allowedFlags[flag]
}

func main() {
	http.HandleFunc("/monitor/commands", monitorHandler)
	fmt.Println("Server starting on port 0.0.0.0:5000")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		fmt.Println("Failed to start server:", err)
	}
}