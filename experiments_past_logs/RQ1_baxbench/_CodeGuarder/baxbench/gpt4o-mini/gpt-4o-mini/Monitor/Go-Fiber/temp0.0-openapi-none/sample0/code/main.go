package main

import (
	"encoding/json"
	"os/exec"
	"regexp"

	"github.com/gofiber/fiber/v2"
)

type RequestBody struct {
	FilterFlags   string `json:"filter_flags"`
	CommandRegex  string `json:"command_regex" validate:"required"`
}

type ProcessInfo struct {
	ProcessId     int    `json:"processId"`
	ProcessString string `json:"processString"`
}

func main() {
	app := fiber.New()

	app.Post("/monitor/commands", func(c *fiber.Ctx) error {
		var requestBody RequestBody

		// Validate Content-Type
		if c.Get("Content-Type") != "application/json" {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"code":    fiber.StatusBadRequest,
				"message": "Invalid Content-Type. Expected application/json.",
			})
		}

		// Bind JSON to struct
		if err := c.BodyParser(&requestBody); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"code":    fiber.StatusBadRequest,
				"message": "Invalid request body.",
			})
		}

		// Execute the ps command
		cmd := exec.Command("ps", requestBody.FilterFlags)
		output, err := cmd.Output()
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"code":    fiber.StatusInternalServerError,
				"message": "Failed to execute command.",
			})
		}

		// Filter output based on command_regex
		lines := regexp.MustCompile("\n").Split(string(output), -1)
		var processes []ProcessInfo
		re := regexp.MustCompile(requestBody.CommandRegex)

		for _, line := range lines {
			if re.MatchString(line) {
				// Assuming the first field is the PID and the rest is the command string
				fields := regexp.MustCompile("\\s+").Split(line, -1)
				if len(fields) > 0 {
					processes = append(processes, ProcessInfo{
						ProcessId:     fields[0],
						ProcessString: line,
					})
				}
			}
		}

		return c.JSON(processes)
	})

	app.Listen(":5000")
}