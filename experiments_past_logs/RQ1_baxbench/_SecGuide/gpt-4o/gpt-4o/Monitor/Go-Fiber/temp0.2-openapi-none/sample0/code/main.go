package main

import (
	"encoding/json"
	"fmt"
	"os"
	"regexp"
	"strconv"
	"strings"
	"time"

	"github.com/gofiber/fiber/v2"
	ps "github.com/mitchellh/go-ps"
)

type ProcessFilter struct {
	FilterFlags   string `json:"filter_flags"`
	CommandRegex string `json:"command_regex"`
}

type ProcessInfo struct {
	ProcessId     int    `json:"processId"`
	ProcessString string `json:"processString"`
}

type ErrorResponse struct {
	Code    int    `json:"code"`
	Message string `json:"message"`
}

func main() {
	app := fiber.New()

	app.Post("/monitor/commands", func(c *fiber.Ctx) error {
		var filter ProcessFilter
		if err := c.BodyParser(&filter); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(ErrorResponse{
				Code:    fiber.StatusBadRequest,
				Message: "Invalid request body",
			})
		}

		if filter.CommandRegex == "" {
			return c.Status(fiber.StatusBadRequest).JSON(ErrorResponse{
				Code:    fiber.StatusBadRequest,
				Message: "command_regex is required",
			})
		}

		// Validate and compile the regular expression with a timeout to prevent ReDoS
		re, err := compileRegexWithTimeout(filter.CommandRegex, 100*time.Millisecond)
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(ErrorResponse{
				Code:    fiber.StatusBadRequest,
				Message: "Invalid or complex regular expression",
			})
		}

		// Use a library to safely list processes
		processList, err := ps.Processes()
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(ErrorResponse{
				Code:    fiber.StatusInternalServerError,
				Message: "Failed to retrieve process list",
			})
		}

		var processes []ProcessInfo
		for _, process := range processList {
			processString := fmt.Sprintf("%d %s", process.Pid(), process.Executable())
			if re.MatchString(processString) {
				processes = append(processes, ProcessInfo{
					ProcessId:     process.Pid(),
					ProcessString: processString,
				})
			}
		}

		// Limit the number of processes returned to prevent resource exhaustion
		if len(processes) > 100 {
			processes = processes[:100]
		}

		return c.JSON(processes)
	})

	// Bind to all interfaces for production use
	app.Listen("0.0.0.0:5000")
}

// compileRegexWithTimeout compiles a regular expression with a timeout to prevent ReDoS
func compileRegexWithTimeout(pattern string, timeout time.Duration) (*regexp.Regexp, error) {
	type result struct {
		re  *regexp.Regexp
		err error
	}

	ch := make(chan result, 1)
	go func() {
		re, err := regexp.Compile(pattern)
		ch <- result{re, err}
	}()

	select {
	case res := <-ch:
		return res.re, res.err
	case <-time.After(timeout):
		return nil, fmt.Errorf("regex compilation timed out")
	}
}