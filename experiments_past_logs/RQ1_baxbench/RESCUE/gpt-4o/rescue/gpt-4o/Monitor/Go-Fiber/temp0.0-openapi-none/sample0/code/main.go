package main

import (
	"encoding/json"
	"log"
	"os/exec"
	"regexp"
	"strings"

	"github.com/gofiber/fiber/v2"
)

type ProcessFilter struct {
	FilterFlags   string `json:"filter_flags"`
	CommandRegex  string `json:"command_regex"`
}

type ProcessInfo struct {
	ProcessID     int    `json:"processId"`
	ProcessString string `json:"processString"`
}

func main() {
	app := fiber.New()

	app.Post("/monitor/commands", func(c *fiber.Ctx) error {
		// Parse the request body
		var filter ProcessFilter
		if err := c.BodyParser(&filter); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"code":    fiber.StatusBadRequest,
				"message": "Invalid request body",
			})
		}

		// Validate the command_regex field
		if filter.CommandRegex == "" {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"code":    fiber.StatusBadRequest,
				"message": "command_regex is required",
			})
		}

		// Compile the regular expression
		regex, err := regexp.Compile(filter.CommandRegex)
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"code":    fiber.StatusBadRequest,
				"message": "Invalid regular expression",
			})
		}

		// Construct the ps command
		psArgs := []string{"-eo", "pid,command"}
		if filter.FilterFlags != "" {
			psArgs = append(psArgs, strings.Fields(filter.FilterFlags)...)
		}

		// Execute the ps command
		cmd := exec.Command("ps", psArgs...)
		output, err := cmd.Output()
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"code":    fiber.StatusInternalServerError,
				"message": "Failed to execute ps command",
			})
		}

		// Parse the output and filter processes
		lines := strings.Split(string(output), "\n")
		var processes []ProcessInfo
		for _, line := range lines {
			line = strings.TrimSpace(line)
			if line == "" || strings.HasPrefix(line, "PID") {
				continue // Skip header or empty lines
			}

			// Split the line into PID and command
			parts := strings.Fields(line)
			if len(parts) < 2 {
				continue // Skip malformed lines
			}

			pid := parts[0]
			command := strings.Join(parts[1:], " ")

			// Match the command against the regex
			if regex.MatchString(command) {
				processes = append(processes, ProcessInfo{
					ProcessID:     parsePID(pid),
					ProcessString: command,
				})
			}
		}

		// Return the filtered processes
		return c.Status(fiber.StatusOK).JSON(processes)
	})

	// Start the server
	log.Fatal(app.Listen("0.0.0.0:5000"))
}

// parsePID safely converts a string to an integer for process ID
func parsePID(pid string) int {
	parsedPID, err := strconv.Atoi(pid)
	if err != nil {
		return 0 // Return 0 for invalid PIDs
	}
	return parsedPID
}