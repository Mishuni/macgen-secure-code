package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os/exec"
	"regexp"
	"strings"

	"github.com/gin-gonic/gin"
)

type ProcessRequest struct {
	FilterFlags   string `json:"filter_flags"`
	CommandRegex  string `json:"command_regex" binding:"required"`
}

type ProcessResponse struct {
	ProcessId     int    `json:"processId"`
	ProcessString string `json:"processString"`
}

type ErrorResponse struct {
	Code    int    `json:"code"`
	Message string `json:"message"`
}

func main() {
	router := gin.Default()

	router.POST("/monitor/commands", func(c *gin.Context) {
		var req ProcessRequest

		// Validate content-type
		if c.GetHeader("Content-Type") != "application/json" {
			c.JSON(http.StatusBadRequest, ErrorResponse{Code: 400, Message: "Invalid content-type"})
			return
		}

		// Parse and validate request body
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, ErrorResponse{Code: 400, Message: "Invalid request body"})
			return
		}

		// Validate and compile the command regex
		commandRegex, err := regexp.Compile(req.CommandRegex)
		if err != nil {
			c.JSON(http.StatusBadRequest, ErrorResponse{Code: 400, Message: "Invalid command regex"})
			return
		}

		// Execute the ps command securely
		output, err := exec.Command("ps", "aux").Output()
		if err != nil {
			c.JSON(http.StatusInternalServerError, ErrorResponse{Code: 500, Message: "Failed to execute command"})
			return
		}

		// Filter and format process data
		lines := strings.Split(string(output), "\n")
		var processes []ProcessResponse
		for _, line := range lines {
			if commandRegex.MatchString(line) {
				fields := strings.Fields(line)
				if len(fields) > 1 {
					processId := fields[1]
					processString := line
					processes = append(processes, ProcessResponse{ProcessId: processId, ProcessString: processString})
				}
			}
		}

		// Respond with the filtered process list
		c.JSON(http.StatusOK, processes)
	})

	// Start the server
	if err := router.Run("0.0.0.0:5000"); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}