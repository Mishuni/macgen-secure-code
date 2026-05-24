package main

import (
	"bytes"
	"encoding/json"
	"net/http"
	"os/exec"
	"regexp"
	"strconv"
	"strings"

	"github.com/gin-gonic/gin"
)

type ProcessFilter struct {
	FilterFlags   string `json:"filter_flags"`
	CommandRegex  string `json:"command_regex" binding:"required"`
}

type Process struct {
	ProcessID     int    `json:"processId"`
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
			c.JSON(http.StatusBadRequest, ErrorResponse{
				Code:    http.StatusBadRequest,
				Message: "Invalid request body: " + err.Error(),
			})
			return
		}

		// Validate the command_regex to ensure it's a valid regex
		_, err := regexp.Compile(filter.CommandRegex)
		if err != nil {
			c.JSON(http.StatusBadRequest, ErrorResponse{
				Code:    http.StatusBadRequest,
				Message: "Invalid regular expression: " + err.Error(),
			})
			return
		}

		// Construct the ps command
		psArgs := []string{"-eo", "pid,command"}
		if filter.FilterFlags != "" {
			psArgs = append(psArgs, strings.Fields(filter.FilterFlags)...)
		}

		// Execute the ps command
		cmd := exec.Command("ps", psArgs...)
		var out bytes.Buffer
		cmd.Stdout = &out
		if err := cmd.Run(); err != nil {
			c.JSON(http.StatusInternalServerError, ErrorResponse{
				Code:    http.StatusInternalServerError,
				Message: "Failed to execute ps command: " + err.Error(),
			})
			return
		}

		// Parse the output of the ps command
		lines := strings.Split(out.String(), "\n")
		var processes []Process
		regex := regexp.MustCompile(filter.CommandRegex)

		for _, line := range lines {
			fields := strings.Fields(line)
			if len(fields) < 2 {
				continue
			}

			// Extract PID and command
			pid, err := strconv.Atoi(fields[0])
			if err != nil {
				continue
			}
			command := strings.Join(fields[1:], " ")

			// Match the command against the regex
			if regex.MatchString(command) {
				processes = append(processes, Process{
					ProcessID:     pid,
					ProcessString: command,
				})
			}
		}

		// Return the filtered processes
		c.JSON(http.StatusOK, processes)
	})

	r.Run("0.0.0.0:5000")
}