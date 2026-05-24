package main

import (
	"encoding/json"
	"net/http"
	"os/exec"
	"regexp"
	"strings"

	"github.com/gin-gonic/gin"
)

type Request struct {
	FilterFlags  string `json:"filter_flags"`
	CommandRegex string `json:"command_regex" binding:"required"`
}

type Process struct {
	ProcessId     int    `json:"processId"`
	ProcessString string `json:"processString"`
}

func main() {
	r := gin.Default()
	r.POST("/monitor/commands", monitorCommands)
	r.Run("0.0.0.0:5000")
}

func monitorCommands(c *gin.Context) {
	var req Request
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"code": 400, "message": "Invalid request"})
		return
	}

	if !isValidRegex(req.CommandRegex) {
		c.JSON(http.StatusBadRequest, gin.H{"code": 400, "message": "Invalid command regex"})
		return
	}

	if !isValidFilterFlags(req.FilterFlags) {
		c.JSON(http.StatusBadRequest, gin.H{"code": 400, "message": "Invalid filter flags"})
		return
	}

	cmd := exec.Command("ps", strings.Fields(req.FilterFlags)...)
	output, err := cmd.Output()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"code": 500, "message": "Failed to execute command"})
		return
	}

	lines := strings.Split(string(output), "\n")
	var processes []Process
	re := regexp.MustCompile(req.CommandRegex)

	for _, line := range lines {
		if re.MatchString(line) {
			fields := strings.Fields(line)
			if len(fields) > 0 {
				processId := fields[0]
				processString := strings.Join(fields[1:], " ")
				processes = append(processes, Process{ProcessId: processId, ProcessString: processString})
			}
		}
	}

	c.JSON(http.StatusOK, processes)
}

func isValidRegex(regex string) bool {
	// Simple validation for regex patterns
	_, err := regexp.Compile(regex)
	return err == nil
}

func isValidFilterFlags(flags string) bool {
	// Basic validation to allow only safe characters
	allowedChars := regexp.MustCompile(`^[\s\w-]+$`)
	return allowedChars.MatchString(flags)
}