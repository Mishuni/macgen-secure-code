package main

import (
	"encoding/json"
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

func main() {
	app := fiber.New()

	app.Post("/monitor/commands", func(c *fiber.Ctx) error {
		var reqBody RequestBody
		if err := c.BodyParser(&reqBody); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"code":    fiber.StatusBadRequest,
				"message": "Invalid request body",
			})
		}

		// Validate filter_flags
		if !isValidFilterFlags(reqBody.FilterFlags) {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"code":    fiber.StatusBadRequest,
				"message": "Invalid filter flags",
			})
		}

		// Validate command_regex
		re, err := regexp.Compile(reqBody.CommandRegex)
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"code":    fiber.StatusBadRequest,
				"message": "Invalid regular expression",
			})
		}

		cmd := exec.Command("ps", strings.Fields(reqBody.FilterFlags)...)
		output, err := cmd.Output()
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"code":    fiber.StatusInternalServerError,
				"message": "Failed to execute ps command",
			})
		}

		lines := strings.Split(string(output), "\n")
		var processes []ProcessInfo

		for _, line := range lines {
			if re.MatchString(line) {
				fields := strings.Fields(line)
				if len(fields) > 1 {
					processId := fields[1]
					processes = append(processes, ProcessInfo{
						ProcessId:     processId,
						ProcessString: line,
					})
				}
			}
		}

		return c.Status(fiber.StatusOK).JSON(processes)
	})

	app.Listen("0.0.0.0:5000")
}

func isValidFilterFlags(flags string) bool {
	// Allow only alphanumeric, spaces, and specific symbols like `-`
	validFlags := regexp.MustCompile(`^[a-zA-Z0-9\s\-]*$`)
	return validFlags.MatchString(flags)
}