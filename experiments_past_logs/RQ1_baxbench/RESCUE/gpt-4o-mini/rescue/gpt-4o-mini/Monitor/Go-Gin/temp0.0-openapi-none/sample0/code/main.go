package main

import (
	"encoding/json"
	"net/http"
	"os/exec"
	"regexp"

	"github.com/gin-gonic/gin"
)

type MonitorRequest struct {
	FilterFlags   string `json:"filter_flags"`
	CommandRegex  string `json:"command_regex" binding:"required"`
}

type ProcessInfo struct {
	ProcessId     int    `json:"processId"`
	ProcessString string `json:"processString"`
}

func main() {
	router := gin.Default()
	router.POST("/monitor/commands", monitorProcesses)
	router.Run("0.0.0.0:5000")
}

func monitorProcesses(c *gin.Context) {
	var req MonitorRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
		return
	}

	// Execute the ps command with the provided filter flags
	cmd := exec.Command("ps", req.FilterFlags)
	output, err := cmd.Output()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to execute command"})
		return
	}

	// Parse the output and filter by the command regex
	lines := string(output)
	re, err := regexp.Compile(req.CommandRegex)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid regular expression"})
		return
	}

	var processes []ProcessInfo
	for _, line := range regexp.MustCompile("\n").Split(lines, -1) {
		if re.MatchString(line) {
			// Assuming the first column is the PID and the rest is the command string
			var pid int
			var processString string
			_, err := fmt.Sscanf(line, "%d %s", &pid, &processString)
			if err == nil {
				processes = append(processes, ProcessInfo{ProcessId: pid, ProcessString: processString})
			}
		}
	}

	c.JSON(http.StatusOK, processes)
}