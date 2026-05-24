package main

import (
	"encoding/json"
	"fmt"
	"log"
	"os/exec"
	"regexp"
	"strings"

	"github.com/gofiber/fiber/v2"
)

type ProcessRequest struct {
	FilterFlags  string `json:"filter_flags"`
	CommandRegex string `json:"command_regex"`
}

type ProcessResponse struct {
	ProcessID     int    `json:"processId"`
	ProcessString string `json:"processString"`
}

type ErrorResponse struct {
	Code    int    `json:"code"`
	Message string `json:"message"`
}

func main() {
	app := fiber.New()

	app.Post("/monitor/commands", func(c *fiber.Ctx) error {
		var req ProcessRequest

		if err := c.BodyParser(&req); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(ErrorResponse{
				Code:    fiber.StatusBadRequest,
				Message: "Invalid request body",
			})
		}

		if req.CommandRegex == "" {
			return c.Status(fiber.StatusBadRequest).JSON(ErrorResponse{
				Code:    fiber.StatusBadRequest,
				Message: "command_regex is required",
			})
		}

		// Validate and compile the regular expression
		commandRegex, err := regexp.Compile(req.CommandRegex)
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(ErrorResponse{
				Code:    fiber.StatusBadRequest,
				Message: "Invalid command_regex",
			})
		}

		// Execute the ps command safely
		cmd := exec.Command("ps", "aux")
		output, err := cmd.Output()
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(ErrorResponse{
				Code:    fiber.StatusInternalServerError,
				Message: "Failed to execute command",
			})
		}

		lines := strings.Split(string(output), "\n")
		var processes []ProcessResponse

		for _, line := range lines {
			if commandRegex.MatchString(line) {
				fields := strings.Fields(line)
				if len(fields) > 1 {
					processID := fields[1]
					processString := line
					processes = append(processes, ProcessResponse{
						ProcessID:     parseProcessID(processID),
						ProcessString: processString,
					})
				}
			}
		}

		return c.JSON(processes)
	})

	log.Fatal(app.Listen("0.0.0.0:5000"))
}

func parseProcessID(pid string) int {
	id, err := strconv.Atoi(pid)
	if err != nil {
		return -1
	}
	return id
}