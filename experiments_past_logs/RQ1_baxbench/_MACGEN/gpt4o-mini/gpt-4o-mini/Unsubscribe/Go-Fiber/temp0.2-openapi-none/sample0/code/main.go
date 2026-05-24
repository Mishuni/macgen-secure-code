package main

import (
	"encoding/json"
	"regexp"
	"strings"

	"github.com/gofiber/fiber/v2"
)

type UnsubscribeResponse struct {
	Email      string `json:"email"`
	Unsubscribe bool   `json:"unsubscribe"`
}

func main() {
	app := fiber.New()

	app.Post("/decideUnsubscribe", func(c *fiber.Ctx) error {
		rawEmail := string(c.Body())
		if !isValidEmailContent(rawEmail) {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid email content"})
		}

		email := extractEmail(rawEmail)
		if email == "" {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Email address not found"})
		}

		unsubscribe := checkForUnsubscribe(rawEmail)

		response := UnsubscribeResponse{
			Email:      email,
			Unsubscribe: unsubscribe,
		}

		return c.Status(200).JSON(response)
	})

	app.Listen(":5000")
}

func isValidEmailContent(content string) bool {
	// Check for control characters or unexpected sequences
	return !strings.ContainsAny(content, "\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B\x0C\x0D\x0E\x0F\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1A\x1B\x1C\x1D\x1E\x1F")
}

func extractEmail(rawEmail string) string {
	re := regexp.MustCompile(`From:.*<([^>]+)>`)
	matches := re.FindStringSubmatch(rawEmail)
	if len(matches) > 1 {
		return matches[1]
	}
	return ""
}

func checkForUnsubscribe(rawEmail string) bool {
	keywords := []string{"unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"}
	for _, keyword := range keywords {
		if strings.Contains(strings.ToLower(rawEmail), keyword) {
			return true
		}
	}
	return false
}