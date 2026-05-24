package main

import (
	"encoding/json"
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
	ProcessId    int    `json:"processId"`
	ProcessString string `json:"processString"`
}

func monitorProcesses(w http.ResponseWriter, r *http.Request) {
	var req MonitorRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	// Validate command_regex
	if _, err := regexp.Compile(req.CommandRegex); err != nil {
		http.Error(w, "Invalid regular expression", http.StatusBadRequest)
		return
	}

	// Execute the ps command with the provided filter flags
	cmd := exec.Command("ps", strings.Fields(req.FilterFlags)...)
	output, err := cmd.Output()
	if err != nil {
		http.Error(w, "Failed to execute ps command", http.StatusInternalServerError)
		return
	}

	// Parse the output and filter by the command regex
	lines := strings.Split(string(output), "\n")
	var processes []ProcessInfo
	re := regexp.MustCompile(req.CommandRegex)

	for _, line := range lines {
		if re.MatchString(line) {
			parts := strings.Fields(line)
			if len(parts) > 1 {
				processId := parts[0]
				processString := strings.Join(parts[1:], " ")
				if id, err := strconv.Atoi(processId); err == nil {
					processes = append(processes, ProcessInfo{ProcessId: id, ProcessString: processString})
				}
			}
		}
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(processes)
}

func main() {
	http.HandleFunc("/monitor/commands", monitorProcesses)
	http.ListenAndServe("0.0.0.0:5000", nil)
}