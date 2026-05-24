package main

import (
    "encoding/json"
    "net/http"
    "os/exec"
    "regexp"
)

type RequestBody struct {
    FilterFlags   string `json:"filter_flags"`
    CommandRegex  string `json:"command_regex"`
}

type ProcessInfo struct {
    ProcessId    int    `json:"processId"`
    ProcessString string `json:"processString"`
}

func monitorProcesses(w http.ResponseWriter, r *http.Request) {
    var requestBody RequestBody

    // Decode the JSON request body
    if err := json.NewDecoder(r.Body).Decode(&requestBody); err != nil {
        http.Error(w, "Invalid request body", http.StatusBadRequest)
        return
    }

    // Execute the ps command with the provided filter flags
    cmd := exec.Command("ps", requestBody.FilterFlags)
    output, err := cmd.Output()
    if err != nil {
        http.Error(w, "Failed to execute command", http.StatusInternalServerError)
        return
    }

    // Use regex to filter the output based on the command_regex
    regex, err := regexp.Compile(requestBody.CommandRegex)
    if err != nil {
        http.Error(w, "Invalid regular expression", http.StatusBadRequest)
        return
    }

    // Parse the output and filter processes
    var processes []ProcessInfo
    lines := string(output)
    for _, line := range regexp.MustCompile("\n").Split(lines, -1) {
        if regex.MatchString(line) {
            // Assuming the first column is the PID
            var pid int
            _, err := fmt.Sscanf(line, "%d", &pid)
            if err == nil {
                processes = append(processes, ProcessInfo{
                    ProcessId:    pid,
                    ProcessString: line,
                })
            }
        }
    }

    // Return the list of matching processes as JSON
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(processes)
}

func main() {
    http.HandleFunc("/monitor/commands", monitorProcesses)
    http.ListenAndServe("0.0.0.0:5000", nil)
}