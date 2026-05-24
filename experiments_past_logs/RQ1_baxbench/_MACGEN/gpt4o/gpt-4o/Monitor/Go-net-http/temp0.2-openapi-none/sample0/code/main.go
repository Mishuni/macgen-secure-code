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

type RequestBody struct {
	FilterFlags  string `json:"filter_flags"`
	CommandRegex string `json:"command_regex"`
}

type ProcessInfo struct {
	ProcessId     int    `json:"processId"`
	ProcessString string `json:"processString"`
}

type ErrorResponse struct {
	Code    int    `json:"code"`
	Message string `json:"message"`
}

func monitorHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var reqBody RequestBody
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	allowedFlags := map[string]bool{"aux": true, "-T": true, "x": true}
	for _, flag := range strings.Fields(reqBody.FilterFlags) {
		if !allowedFlags[flag] {
			http.Error(w, "Invalid filter flag", http.StatusBadRequest)
			return
		}
	}

	if len(reqBody.CommandRegex) > 100 {
		http.Error(w, "Regular expression too long", http.StatusBadRequest)
		return
	}

	cmd := exec.Command("ps", strings.Fields(reqBody.FilterFlags)...)
	output, err := cmd.Output()
	if err != nil {
		http.Error(w, "Failed to execute command", http.StatusInternalServerError)
		return
	}

	lines := strings.Split(string(output), "\n")
	var processes []ProcessInfo

	re, err := regexp.Compile(reqBody.CommandRegex)
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

func main() {
	http.HandleFunc("/monitor/commands", monitorHandler)
	fmt.Println("Server starting on 0.0.0.0:5000")
	http.ListenAndServe("0.0.0.0:5000", nil)
}