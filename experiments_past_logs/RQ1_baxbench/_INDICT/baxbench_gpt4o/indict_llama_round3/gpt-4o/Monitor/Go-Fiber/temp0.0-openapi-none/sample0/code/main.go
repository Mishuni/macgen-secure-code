package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"os/exec"
	"regexp"
	"strconv"
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

		if reqBody.CommandRegex == "" {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"code":    fiber.StatusBadRequest,
				"message": "command_regex is required",
			})
		}

		// Validate and sanitize filter flags
		filterFlags := strings.Fields(reqBody.FilterFlags)
		for _, flag := range filterFlags {
			if !isValidFlag(flag) {
				return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
					"code":    fiber.StatusBadRequest,
					"message": fmt.Sprintf("Invalid filter flag: %s", flag),
				})
			}
		}

		cmd := exec.Command("ps", append([]string{"aux"}, filterFlags...)...)
		var out bytes.Buffer
		cmd.Stdout = &out
		if err := cmd.Run(); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"code":    fiber.StatusInternalServerError,
				"message": "Failed to execute ps command",
			})
		}

		lines := strings.Split(out.String(), "\n")
		var processes []ProcessInfo
		regex, err := regexp.Compile(reqBody.CommandRegex)
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"code":    fiber.StatusBadRequest,
				"message": "Invalid command_regex",
			})
		}

		for _, line := range lines[1:] {
			if regex.MatchString(line) {
				fields := strings.Fields(line)
				if len(fields) < 2 {
					continue
				}
				pid, err := strconv.Atoi(fields[1])
				if err != nil {
					continue
				}
				processes = append(processes, ProcessInfo{
					ProcessId:     pid,
					ProcessString: line,
				})
			}
		}

		return c.JSON(processes)
	})

	app.Listen("0.0.0.0:5000")
}

func isValidFlag(flag string) bool {
	// Define a set of allowed flags for safety
	allowedFlags := map[string]bool{
		"-T": true,
		"x":  true,
	}
	return allowedFlags[flag]
}