package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os/exec"
	"regexp"
	"strconv"
	"strings"
)

type ProcessRequest struct {
	FilterFlags  string `json:"filter_flags"`
	CommandRegex string `json:"command_regex"`
}

type ProcessResponse struct {
	ProcessId     int    `json:"processId"`
	ProcessString string `json:"processString"`
}

type ErrorResponse struct {
	Code    int    `json:"code"`
	Message string `json:"message"`
}

func main() {
	http.HandleFunc("/monitor/commands", monitorHandler)
	log.Println("Starting server on :5000")
	log.Fatal(http.ListenAndServe("0.0.0.0:5000", nil))
}

func monitorHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req ProcessRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	if !isValidRegex(req.CommandRegex) {
		http.Error(w, "Invalid command regex", http.StatusBadRequest)
		return
	}

	if !isValidFilterFlags(req.FilterFlags) {
		http.Error(w, "Invalid filter flags", http.StatusBadRequest)
		return
	}

	processes, err := getProcesses(req.FilterFlags, req.CommandRegex)
	if err != nil {
		http.Error(w, "Error retrieving processes", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(processes)
}

func isValidRegex(pattern string) bool {
	// Limit regex complexity to prevent ReDoS
	if len(pattern) > 100 {
		return false
	}
	_, err := regexp.Compile(pattern)
	return err == nil
}

func isValidFilterFlags(flags string) bool {
	// Allow only specific safe flags
	allowedFlags := map[string]bool{
		"-e": true,
		"-f": true,
		"-l": true,
	}
	for _, flag := range strings.Fields(flags) {
		if !allowedFlags[flag] {
			return false
		}
	}
	return true
}

func getProcesses(filterFlags, commandRegex string) ([]ProcessResponse, error) {
	// Use a safer approach to execute the command
	cmd := exec.Command("ps", strings.Fields(filterFlags)...)
	output, err := cmd.Output()
	if err != nil {
		return nil, fmt.Errorf("failed to execute command: %w", err)
	}

	lines := strings.Split(string(output), "\n")
	var processes []ProcessResponse
	for _, line := range lines {
		if matched, _ := regexp.MatchString(commandRegex, line); matched {
			fields := strings.Fields(line)
			if len(fields) > 1 {
				processId, err := strconv.Atoi(fields[1])
				if err != nil {
					continue
				}
				processString := strings.Join(fields, " ")
				processes = append(processes, ProcessResponse{
					ProcessId:     processId,
					ProcessString: processString,
				})
			}
		}
	}
	return processes, nil
}