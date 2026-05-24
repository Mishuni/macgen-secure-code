package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os/exec"
	"regexp"
	"strings"
)

type ProcessFilterRequest struct {
	FilterFlags   string `json:"filter_flags"`
	CommandRegex  string `json:"command_regex"`
}

type ProcessResponse struct {
	ProcessID     int    `json:"processId"`
	ProcessString string `json:"processString"`
}

type ErrorResponse struct {
	Code    int    `json:"code"`
	Message string `json:"message"`
}

func main() {
	http.HandleFunc("/monitor/commands", handleMonitorCommands)
	fmt.Println("Starting server on 0.0.0.0:5000...")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		fmt.Printf("Error starting server: %v\n", err)
	}
}

func handleMonitorCommands(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		writeErrorResponse(w, http.StatusMethodNotAllowed, "Method not allowed")
		return
	}

	var filterRequest ProcessFilterRequest
	if err := json.NewDecoder(r.Body).Decode(&filterRequest); err != nil {
		writeErrorResponse(w, http.StatusBadRequest, "Invalid request body")
		return
	}

	if filterRequest.CommandRegex == "" {
		writeErrorResponse(w, http.StatusBadRequest, "command_regex is required")
		return
	}

	// Validate the provided regular expression
	commandRegex, err := regexp.Compile(filterRequest.CommandRegex)
	if err != nil {
		writeErrorResponse(w, http.StatusBadRequest, "Invalid regular expression")
		return
	}

	// Construct the ps command arguments
	psArgs := []string{"-eo", "pid,command"}
	if filterRequest.FilterFlags != "" {
		psArgs = append(psArgs, strings.Fields(filterRequest.FilterFlags)...)
	}

	// Execute the ps command securely
	cmd := exec.Command("ps", psArgs...)
	output, err := cmd.Output()
	if err != nil {
		writeErrorResponse(w, http.StatusInternalServerError, "Failed to execute ps command")
		return
	}

	// Parse the output and filter processes
	lines := strings.Split(string(output), "\n")
	var processes []ProcessResponse
	for _, line := range lines {
		line = strings.TrimSpace(line)
		if line == "" || strings.HasPrefix(line, "PID") {
			continue
		}

		parts := strings.Fields(line)
		if len(parts) < 2 {
			continue
		}

		pid := parts[0]
		command := strings.Join(parts[1:], " ")

		// Match the command string against the provided regex
		if commandRegex.MatchString(command) {
			processID, err := parsePID(pid)
			if err != nil {
				continue
			}
			processes = append(processes, ProcessResponse{
				ProcessID:     processID,
				ProcessString: command,
			})
		}
	}

	// Write the response
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	if err := json.NewEncoder(w).Encode(processes); err != nil {
		fmt.Printf("Error writing response: %v\n", err)
	}
}

func parsePID(pid string) (int, error) {
	return strconv.Atoi(pid)
}

func writeErrorResponse(w http.ResponseWriter, code int, message string) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(code)
	json.NewEncoder(w).Encode(ErrorResponse{
		Code:    code,
		Message: message,
	})
}