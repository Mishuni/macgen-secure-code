package main

import (
	"encoding/json"
	"fmt"
	"os/exec"
	"regexp"
	"strings"

	"github.com/gofiber/fiber/v2"
)

type RequestBody struct {
	FilterFlags  string `json:"filter_flags"`
	CommandRegex string `json:"command_regex"`
}

type ProcessInfo struct {
	ProcessId     int    `json:"processId"`
	ProcessString string `json:"processString"`
}

func isValidFilterFlags(flags string) bool {
	// Allow only specific flags (e.g., -e, -f) to prevent command injection
	validFlags := []string{"-e", "-f"}
	for _, flag := range validFlags {
		if strings.Contains(flags, flag) {
			// Ensure that only valid flags are present
			// Split flags and check each one
			for _, f := range strings.Fields(flags) {
				if !contains(validFlags, f) {
					return false
				}
			}
			return true
		}
	}
	return false
}

func contains(slice []string, item string) bool {
	for _, v := range slice {
		if v == item {
			return true
		}
	}
	return false
}

func isValidCommandRegex(regex string) bool {
	// Basic validation to prevent overly complex regex patterns
	if len(regex) > 100 { // Limit regex length
		return false
	}
	// Check for patterns that could lead to catastrophic backtracking
	// This is a simple check; more complex patterns can be added as needed
	if strings.Contains(regex, "(?") {
		return false
	}
	return true
}

func main() {
	app := fiber.New()

	app.Post("/monitor/commands", func(c *fiber.Ctx) error {
		var reqBody RequestBody
		if err := c.BodyParser(&reqBody); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"code": 400, "message": "Invalid request body"})
		}

		if !isValidFilterFlags(reqBody.FilterFlags) {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"code": 400, "message": "Invalid filter flags"})
		}

		if !isValidCommandRegex(reqBody.CommandRegex) {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"code": 400, "message": "Invalid command regex"})
		}

		// Execute the ps command with the provided filter flags
		cmd := exec.Command("ps", strings.Fields(reqBody.FilterFlags)...)
		output, err := cmd.Output()
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"code": 500, "message": "Failed to execute command"})
		}

		// Filter processes based on the command regex
		lines := string(output)
		re, err := regexp.Compile(reqBody.CommandRegex)
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"code": 400, "message": "Invalid command regex"})
		}

		var processes []ProcessInfo
		for _, line := range strings.Split(lines, "\n") {
			if re.MatchString(line) {
				// Assuming the first column is the PID and the rest is the command string
				var pid int
				var command string
				_, err := fmt.Sscanf(line, "%d %s", &pid, &command)
				if err == nil {
					processes = append(processes, ProcessInfo{ProcessId: pid, ProcessString: line})
				}
			}
		}

		// Sanitize output before sending it to the client
		for i := range processes {
			processes[i].ProcessString = sanitizeOutput(processes[i].ProcessString)
		}

		return c.JSON(processes)
	})

	app.Listen("0.0.0.0:5000")
}

func sanitizeOutput(output string) string {
	// Basic sanitization to prevent XSS or other injection attacks
	return strings.ReplaceAll(output, "<", "&lt;")
}