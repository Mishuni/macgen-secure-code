package main

import (
	"encoding/json"
	"os/exec"
	"regexp"
	"strings"

	"github.com/gofiber/fiber/v2"
)

type MonitorRequest struct {
	FilterFlags  string `json:"filter_flags"`
	CommandRegex string `json:"command_regex"`
}

type ProcessInfo struct {
	ProcessId     int    `json:"processId"`
	ProcessString string `json:"processString"`
}

func main() {
	app := fiber.New()

	app.Post("/monitor/commands", func(c *fiber.Ctx) error {
		var req MonitorRequest
		if err := c.BodyParser(&req); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"code": 400, "message": "Invalid request"})
		}

		// Validate command_regex to prevent DoS attacks
		if _, err := regexp.Compile(req.CommandRegex); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"code": 400, "message": "Invalid regular expression"})
		}

		// Split filter flags into separate arguments
		filterArgs := strings.Fields(req.FilterFlags)
		cmd := exec.Command("ps", filterArgs...)
		output, err := cmd.Output()
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"code": 500, "message": "Failed to execute command"})
		}

		lines := strings.Split(string(output), "\n")
		var processes []ProcessInfo
		re := regexp.MustCompile(req.CommandRegex)

		for _, line := range lines {
			if re.MatchString(line) {
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