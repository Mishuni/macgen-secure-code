package main

import (
	"encoding/json"
	"fmt"
	"os/exec"
	"regexp"
	"strconv"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
)

type ProcessRequest struct {
	FilterFlags  string `json:"filter_flags"`
	CommandRegex string `json:"command_regex" binding:"required"`
}

type ProcessResponse struct {
	ProcessId     int    `json:"processId"`
	ProcessString string `json:"processString"`
}

func main() {
	r := gin.Default()

	r.POST("/monitor/commands", func(c *gin.Context) {
		var req ProcessRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(400, gin.H{"error": "Invalid request"})
			return
		}

		// Validate and sanitize the FilterFlags input
		if !isValidFilterFlags(req.FilterFlags) {
			c.JSON(400, gin.H{"error": "Invalid filter flags"})
			return
		}

		// Validate the regular expression with a timeout
		if !isValidRegex(req.CommandRegex) {
			c.JSON(400, gin.H{"error": "Invalid or unsafe regular expression"})
			return
		}

		// Execute the ps command
		cmd := exec.Command("ps", strings.Fields(req.FilterFlags)...)
		output, err := cmd.Output()
		if err != nil {
			c.JSON(500, gin.H{"error": "Failed to execute command"})
			return
		}

		// Filter processes based on the command regex
		lines := strings.Split(string(output), "\n")
		var processes []ProcessResponse
		for _, line := range lines {
			matched, err := regexp.MatchString(req.CommandRegex, line)
			if err != nil {
				c.JSON(500, gin.H{"error": "Error processing regex"})
				return
			}
			if matched {
				fields := strings.Fields(line)
				if len(fields) > 1 {
					processId := fields[1]
					processString := line
					if pid, err := parseProcessId(processId); err == nil {
						processes = append(processes, ProcessResponse{
							ProcessId:     pid,
							ProcessString: processString,
						})
					}
				}
			}
		}

		c.JSON(200, processes)
	})

	r.Run("0.0.0.0:5000")
}

func isValidFilterFlags(flags string) bool {
	// Implement a whitelist of allowed flags
	allowedFlags := map[string]bool{
		"-e": true,
		"-f": true,
		// Add more allowed flags as needed
	}

	for _, flag := range strings.Fields(flags) {
		if !allowedFlags[flag] {
			return false
		}
	}
	return true
}

func isValidRegex(pattern string) bool {
	// Compile the regex with a timeout to prevent ReDoS
	done := make(chan bool, 1)
	go func() {
		_, err := regexp.Compile(pattern)
		done <- err == nil
	}()

	select {
	case valid := <-done:
		return valid
	case <-time.After(1 * time.Second):
		return false
	}
}

func parseProcessId(pid string) (int, error) {
	return strconv.Atoi(pid)
}