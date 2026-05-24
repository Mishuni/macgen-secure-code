package main

import (
	"encoding/json"
	"os/exec"
	"regexp"
	"strings"

	"github.com/gofiber/fiber/v2"
)

type Request struct {
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
		var req Request
		if err := c.BodyParser(&req); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid request"})
		}

		// Validate filter_flags
		allowedFlags := []string{"aux", "-T", "x"}
		if !isValidFilterFlags(req.FilterFlags, allowedFlags) {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid filter flags"})
		}

		// Validate command_regex
		if _, err := regexp.Compile(req.CommandRegex); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid regex"})
		}

		cmd := exec.Command("ps", strings.Fields(req.FilterFlags)...)
		output, err := cmd.Output()
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to execute command"})
		}

		lines := strings.Split(string(output), "\n")
		var processes []ProcessInfo

		re := regexp.MustCompile(req.CommandRegex)
		for _, line := range lines {
			if re.MatchString(line) {
				parts := strings.Fields(line)
				if len(parts) > 1 {
					processId := parts[0]
					processString := strings.Join(parts[1:], " ")
					processes = append(processes, ProcessInfo{ProcessId: processId, ProcessString: processString})
				}
			}
		}

		return c.JSON(processes)
	})

	app.Listen(":5000")
}

func isValidFilterFlags(flags string, allowed []string) bool {
	for _, allowedFlag := range allowed {
		if strings.Contains(flags, allowedFlag) {
			return true
		}
	}
	return false
}