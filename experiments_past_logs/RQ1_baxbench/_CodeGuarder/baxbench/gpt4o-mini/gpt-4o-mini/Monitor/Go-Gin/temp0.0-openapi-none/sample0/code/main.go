package main

import (
	"encoding/json"
	"fmt"
	"os/exec"
	"regexp"

	"github.com/gin-gonic/gin"
)

type RequestBody struct {
	FilterFlags   string `json:"filter_flags"`
	CommandRegex  string `json:"command_regex" binding:"required"`
}

type ProcessInfo struct {
	ProcessId     int    `json:"processId"`
	ProcessString string `json:"processString"`
}

type ErrorResponse struct {
	Code    int    `json:"code"`
	Message string `json:"message"`
}

func main() {
	router := gin.Default()
	router.POST("/monitor/commands", monitorCommands)
	router.Run("0.0.0.0:5000")
}

func monitorCommands(c *gin.Context) {
	var requestBody RequestBody
	if err := c.ShouldBindJSON(&requestBody); err != nil {
		c.JSON(400, ErrorResponse{Code: 400, Message: "Invalid request body"})
		return
	}

	// Validate the command_regex
	if _, err := regexp.Compile(requestBody.CommandRegex); err != nil {
		c.JSON(400, ErrorResponse{Code: 400, Message: "Invalid command_regex"})
		return
	}

	// Execute the ps command
	cmd := exec.Command("ps", requestBody.FilterFlags)
	output, err := cmd.Output()
	if err != nil {
		c.JSON(500, ErrorResponse{Code: 500, Message: "Failed to execute ps command"})
		return
	}

	// Filter processes based on command_regex
	var processes []ProcessInfo
	lines := string(output)
	for _, line := range regexp.MustCompile("\n").Split(lines, -1) {
		if matched, _ := regexp.MatchString(requestBody.CommandRegex, line); matched {
			// Assuming the first column is the PID and the rest is the command string
			var processId int
			var processString string
			fmt.Sscanf(line, "%d %s", &processId, &processString)
			processes = append(processes, ProcessInfo{ProcessId: processId, ProcessString: processString})
		}
	}

	c.JSON(200, processes)
}