package main

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"os/exec"
	"regexp"
	"strconv"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
)

type MonitorRequest struct {
	FilterFlags  string `json:"filter_flags"`
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

func isValidRegex(pattern string) bool {
	// Simple validation to prevent ReDoS attacks
	// This can be extended with more complex checks if needed
	_, err := regexp.Compile(pattern)
	return err == nil
}

func main() {
	r := gin.Default()

	r.POST("/monitor/commands", func(c *gin.Context) {
		var req MonitorRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(400, ErrorResponse{Code: 400, Message: "Invalid request"})
			return
		}

		// Validate filter_flags
		allowedFlags := map[string]bool{"aux": true, "-T": true, "x": true}
		for _, flag := range strings.Fields(req.FilterFlags) {
			if !allowedFlags[flag] {
				c.JSON(400, ErrorResponse{Code: 400, Message: "Invalid filter flag"})
				return
			}
		}

		// Validate command_regex
		if !isValidRegex(req.CommandRegex) {
			c.JSON(400, ErrorResponse{Code: 400, Message: "Invalid regex pattern"})
			return
		}

		// Execute the ps command
		ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()
		cmd := exec.CommandContext(ctx, "ps", strings.Fields(req.FilterFlags)...)
		var out bytes.Buffer
		cmd.Stdout = &out
		if err := cmd.Run(); err != nil {
			c.JSON(500, ErrorResponse{Code: 500, Message: "Failed to execute command"})
			return
		}

		re, err := regexp.Compile(req.CommandRegex)
		if err != nil {
			c.JSON(400, ErrorResponse{Code: 400, Message: "Invalid regex"})
			return
		}

		lines := strings.Split(out.String(), "\n")
		var processes []ProcessInfo
		for _, line := range lines {
			if re.MatchString(line) {
				fields := strings.Fields(line)
				if len(fields) > 1 {
					if pid, err := strconv.Atoi(fields[1]); err == nil {
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