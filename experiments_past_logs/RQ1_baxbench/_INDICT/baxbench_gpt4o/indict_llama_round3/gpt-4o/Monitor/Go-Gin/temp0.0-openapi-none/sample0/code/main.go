package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"os/exec"
	"regexp"
	"strconv"
	"strings"

	"github.com/gin-gonic/gin"
)

type ProcessFilter struct {
	FilterFlags   string `json:"filter_flags"`
	CommandRegex string `json:"command_regex" binding:"required"`
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
	r := gin.Default()

	r.POST("/monitor/commands", func(c *gin.Context) {
		var filter ProcessFilter
		if err := c.ShouldBindJSON(&filter); err != nil {
			c.JSON(400, ErrorResponse{Code: 400, Message: "Invalid request body"})
			return
		}

		// Validate filter flags to prevent command injection
		if !isValidFilterFlags(filter.FilterFlags) {
			c.JSON(400, ErrorResponse{Code: 400, Message: "Invalid filter flags"})
			return
		}

		cmd := exec.Command("ps", strings.Fields(filter.FilterFlags)...)
		var out bytes.Buffer
		cmd.Stdout = &out
		if err := cmd.Run(); err != nil {
			c.JSON(500, ErrorResponse{Code: 500, Message: "Failed to execute ps command"})
			return
		}

		lines := strings.Split(out.String(), "\n")
		var processes []ProcessInfo
		regex, err := regexp.Compile(filter.CommandRegex)
		if err != nil {
			c.JSON(400, ErrorResponse{Code: 400, Message: "Invalid regular expression"})
			return
		}

		for _, line := range lines {
			if regex.MatchString(line) {
				fields := strings.Fields(line)
				if len(fields) > 0 {
					pid, err := strconv.Atoi(fields[0]) // Adjusted to use the correct field for PID
					if err == nil {
						processes = append(processes, ProcessInfo{
							ProcessId:     pid,
							ProcessString: line,
						})
					}
				}
			}
		}

		c.JSON(200, processes)
	})

	r.Run("0.0.0.0:5000")
}

// isValidFilterFlags checks if the provided filter flags are valid
func isValidFilterFlags(flags string) bool {
	// Allow only specific flags to prevent command injection
	allowedFlags := map[string]bool{
		"aux": true,
		"x":   true,
		"T":   true,
	}
	for _, flag := range strings.Fields(flags) {
		if !allowedFlags[flag] {
			return false
		}
	}
	return true
}