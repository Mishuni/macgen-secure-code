package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os/exec"
	"regexp"
	"strings"
)

type ProcessRequest struct {
	FilterFlags  string `json:"filter_flags"`
	CommandRegex string `json:"command_regex"`
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
	http.HandleFunc("/monitor/commands", monitorHandler)
	log.Fatal(http.ListenAndServe("0.0.0.0:5000", nil))
}

func monitorHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	if r.Header.Get("Content-Type") != "application/json" {
		http.Error(w, "Invalid content-type", http.StatusBadRequest)
		return
	}

	var req ProcessRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	if req.CommandRegex == "" {
		http.Error(w, "command_regex is required", http.StatusBadRequest)
		return
	}

	cmd := exec.Command("ps", strings.Fields(req.FilterFlags)...)
	output, err := cmd.Output()
	if err != nil {
		http.Error(w, "Failed to execute command", http.StatusInternalServerError)
		return
	}

	lines := strings.Split(string(output), "\n")
	var processes []ProcessResponse
	re, err := regexp.Compile(req.CommandRegex)
	if err != nil {
		http.Error(w, "Invalid regular expression", http.StatusBadRequest)
		return
	}

	for _, line := range lines {
		if re.MatchString(line) {
			fields := strings.Fields(line)
			if len(fields) > 1 {
				processID := fields[0]
				processString := strings.Join(fields[1:], " ")
				processes = append(processes, ProcessResponse{
					ProcessID:     parseProcessID(processID),
					ProcessString: processString,
				})
			}
		}
	}

	w.Header().Set("Content-Type", "application/json")
	if err := json.NewEncoder(w).Encode(processes); err != nil {
		http.Error(w, "Failed to encode response", http.StatusInternalServerError)
	}
}

func parseProcessID(pid string) int {
	id, err := strconv.Atoi(pid)
	if err != nil {
		return -1
	}
	return id
}