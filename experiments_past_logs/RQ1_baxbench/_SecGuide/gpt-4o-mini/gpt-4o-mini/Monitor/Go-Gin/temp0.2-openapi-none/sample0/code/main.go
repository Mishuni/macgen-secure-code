package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os/exec"
	"regexp"
	"strings"

	"github.com/gin-gonic/gin"
)

type RequestBody struct {
	FilterFlags  string `json:"filter_flags"`
	CommandRegex string `json:"command_regex" binding:"required"`
}

type ProcessInfo struct {
	ProcessId     int    `json:"processId"`
	ProcessString string `json:"processString"`
}

func main() {
	r := gin.Default()
	r.POST("/monitor/commands", monitorProcesses)
	r.Run("0.0.0.0:5000")
}

func monitorProcesses(c *gin.Context) {
	var requestBody RequestBody
	if err := c.ShouldBindJSON(&requestBody); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"code": 400, "message": "Invalid request body"})
		return
	}

	// Validate FilterFlags to allow only safe characters
	if !isValidFilterFlags(requestBody.FilterFlags) {
		c.JSON(http.StatusBadRequest, gin.H{"code": 400, "message": "Invalid filter flags"})
		return
	}

	// Execute the ps command with the provided filter flags
	cmd := exec.Command("ps", strings.Fields(requestBody.FilterFlags)...)
	output, err := cmd.Output()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"code": 500, "message": "Failed to execute command"})
		return
	}

	// Filter processes based on the command regex
	commandRegex, err := regexp.Compile(requestBody.CommandRegex)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"code": 400, "message": "Invalid command regex"})
		return
	}

	var processes []ProcessInfo
	lines := strings.Split(string(output), "\n")
	for _, line := range lines {
		if commandRegex.MatchString(line) {
			// Extract process ID and command string from the line
			var processId int
			var processString string
			_, err := fmt.Sscanf(line, "%d %s", &processId, &processString)
			if err == nil {
				processes = append(processes, ProcessInfo{ProcessId: processId, ProcessString: sanitizeOutput(line)})
			}
		}
	}

	c.JSON(http.StatusOK, processes)
}

// isValidFilterFlags checks if the filter flags contain only safe characters
func isValidFilterFlags(flags string) bool {
	// Allow only alphanumeric characters and specific safe symbols
	re := regexp.MustCompile(`^[\w\s-]*$`)
	return re.MatchString(flags)
}

// sanitizeOutput ensures that the output does not contain sensitive information
func sanitizeOutput(output string) string {
	// Implement sanitization logic to remove sensitive information
	// For example, we can limit the output to a certain length or remove specific patterns
	return output // For now, just return the output as is
}