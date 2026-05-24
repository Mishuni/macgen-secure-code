package main

import (
	"encoding/json"
	"net/http"
	"os"
	"os/exec"
	"regexp"
	"strings"

	"github.com/gin-gonic/gin"
)

type MonitorRequest struct {
	FilterFlags  string `json:"filter_flags"`
	CommandRegex string `json:"command_regex" binding:"required"`
}

type ProcessInfo struct {
	ProcessId    int    `json:"processId"`
	ProcessString string `json:"processString"`
}

func main() {
	r := gin.Default()
	r.POST("/monitor/commands", monitorCommands)
	r.Run("0.0.0.0:5000")
}

func monitorCommands(c *gin.Context) {
	var req MonitorRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
		return
	}

	// Execute the ps command with the provided filter flags
	cmd := exec.Command("ps", strings.Fields(req.FilterFlags)...)
	output, err := cmd.Output()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to execute command"})
		return
	}

	lines := strings.Split(string(output), "\n")
	var processes []ProcessInfo
	re := regexp.MustCompile(req.CommandRegex)

	for _, line := range lines {
		if re.MatchString(line) {
			parts := strings.Fields(line)
			if len(parts) > 1 {
				processId := parts[1]
				processString := strings.Join(parts[1:], " ")
				processes = append(processes, ProcessInfo{ProcessId: processId, ProcessString: processString})
			}
		}
	}

	c.JSON(http.StatusOK, processes)
}