package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os/exec"
	"regexp"
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

var safeFlags = map[string]bool{
	"aux": true,
	"T":   true,
	"x":   true,
}

func isValidFilterFlags(flags string) bool {
	for _, flag := range strings.Fields(flags) {
		if !safeFlags[flag] {
			return false
		}
	}
	return true
}

func monitorCommandsHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var reqBody RequestBody
	body, err := ioutil.ReadAll(r.Body)
	if err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	if err := json.Unmarshal(body, &reqBody); err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}

	if !isValidFilterFlags(reqBody.FilterFlags) {
		http.Error(w, "Invalid filter flags", http.StatusBadRequest)
		return
	}

	if len(reqBody.CommandRegex) > 100 {
		http.Error(w, "Regex too complex", http.StatusBadRequest)
		return
	}

	re, err := regexp.Compile(reqBody.CommandRegex)
	if err != nil {
		http.Error(w, "Invalid regular expression", http.StatusBadRequest)
		return
	}

	cmd := exec.Command("ps", strings.Fields(reqBody.FilterFlags)...)
	output, err := cmd.Output()
	if err != nil {
		http.Error(w, "Failed to execute command", http.StatusInternalServerError)
		return
	}

	lines := strings.Split(string(output), "\n")
	var results []ProcessInfo

	for _, line := range lines {
		if re.MatchString(line) {
			fields := strings.Fields(line)
			if len(fields) > 1 {
				var pid int
				fmt.Sscanf(fields[1], "%d", &pid)
				results = append(results, ProcessInfo{ProcessId: pid, ProcessString: line})
			}
		}
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(results)
}

func main() {
	http.HandleFunc("/monitor/commands", monitorCommandsHandler)
	http.ListenAndServe("0.0.0.0:5000", nil)
}