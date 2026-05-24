package main

import (
	"encoding/json"
	"fmt"
	"os/exec"
	"regexp"

	"github.com/gofiber/fiber/v2"
)

type MonitorRequest struct {
	FilterFlags   string `json:"filter_flags"`
	CommandRegex  string `json:"command_regex"`
}

type ProcessInfo struct {
	ProcessId    int    `json:"processId"`
	ProcessString string `json:"processString"`
}

func main() {
	app := fiber.New()

	app.Post("/monitor/commands", func(c *fiber.Ctx) error {
		var req MonitorRequest
		if err := c.BodyParser(&req); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"code": 400, "message": "Invalid request body"})
		}

		// Validate the command regex
		if _, err := regexp.Compile(req.CommandRegex); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"code": 400, "message": "Invalid command regex"})
		}

		// Execute the ps command with the provided filter flags
		cmd := exec.Command("ps", req.FilterFlags)
		output, err := cmd.Output()
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"code": 500, "message": "Failed to execute command"})
		}

		// Parse the output and filter by the command regex
		lines := string(output)
		var processes []ProcessInfo
		for _, line := range regexp.MustCompile("\n").Split(lines, -1) {
			if matched, _ := regexp.MatchString(req.CommandRegex, line); matched {
				// Assuming the first column is the PID and the rest is the command string
				var pid int
				var processString string
				_, err := fmt.Sscanf(line, "%d %s", &pid, &processString)
				if err == nil {
					processes = append(processes, ProcessInfo{ProcessId: pid, ProcessString: processString})
				}
			}
		}

		return c.JSON(processes)
	})

	app.Listen(":5000")
}