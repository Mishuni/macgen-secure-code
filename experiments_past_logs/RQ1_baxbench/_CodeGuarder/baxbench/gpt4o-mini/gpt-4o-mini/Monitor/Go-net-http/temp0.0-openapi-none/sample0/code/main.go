package main

import (
	"encoding/json"
	"fmt"
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
	ProcessId     int    `json:"processId"`
	ProcessString string `json:"processString"`
}

func main() {
	http.HandleFunc("/monitor/commands", handleCommands)
	http.ListenAndServe("0.0.0.0:5000", nil)
}

func handleCommands(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	if r.Header.Get("Content-Type") != "application/json" {
		http.Error(w, "Invalid Content-Type", http.StatusBadRequest)
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

	processes, err := getMatchingProcesses(requestBody.FilterFlags, requestBody.CommandRegex)
	if err != nil {
		http.Error(w, fmt.Sprintf("Error retrieving processes: %v", err), http.StatusInternalServerError)
		return
	}

	response, err := json.Marshal(processes)
	if err != nil {
		http.Error(w, "Error generating response", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	w.Write(response)
}

func getMatchingProcesses(filterFlags, commandRegex string) ([]ProcessInfo, error) {
	cmd := exec.Command("ps", strings.Fields(filterFlags)...)
	output, err := cmd.Output()
	if err != nil {
		return nil, err
	}

	lines := strings.Split(string(output), "\n")
	var processes []ProcessInfo
	re, err := regexp.Compile(commandRegex)
	if err != nil {
		return nil, err
	}

	for _, line := range lines {
		if re.MatchString(line) {
			parts := strings.Fields(line)
			if len(parts) > 0 {
				processId := parts[0]
				processString := strings.Join(parts[1:], " ")
				processes = append(processes, ProcessInfo{ProcessId: processId, ProcessString: processString})
			}
		}
	}

	return processes, nil
}