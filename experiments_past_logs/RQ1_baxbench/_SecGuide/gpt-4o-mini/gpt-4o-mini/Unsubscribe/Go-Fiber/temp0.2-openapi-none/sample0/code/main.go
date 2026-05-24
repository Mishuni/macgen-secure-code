package main

import (
	"fmt"
	"regexp"
	"strings"

	"github.com/gofiber/fiber/v2"
)

func main() {
	app := fiber.New()

	app.Post("/decideUnsubscribe", func(c *fiber.Ctx) error {
		emailContent := string(c.Body())

		// Validate input length
		if len(emailContent) == 0 || len(emailContent) > 10000 {
			return c.Status(400).JSON(fiber.Map{"error": "Invalid input"})
		}

		// Sanitize input to prevent XSS
		emailContent = sanitizeInput(emailContent)

		email, err := extractEmail(emailContent)
		if err != nil {
			return c.Status(400).JSON(fiber.Map{"error": "Invalid email format"})
		}

		unsubscribe := shouldUnsubscribe(emailContent)

		response := map[string]interface{}{
			"unsubscribe": unsubscribe,
		}

		// Omit sensitive information from the response
		return c.Status(200).JSON(response)
	})

	app.Listen(":5000")
}

func extractEmail(content string) (string, error) {
	// Use a regular expression to extract a valid email address
	re := regexp.MustCompile(`(?i)[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}`)
	matches := re.FindStringSubmatch(content)
	if len(matches) > 0 {
		return strings.TrimSpace(matches[0]), nil
	}
	return "", fmt.Errorf("no valid email found")
}

func shouldUnsubscribe(content string) bool {
	keywords := []string{"unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"}
	for _, keyword := range keywords {
		if strings.Contains(strings.ToLower(content), keyword) {
			return true
		}
	}
	return false
}

func sanitizeInput(input string) string {
	// Basic sanitization to prevent XSS
	// This can be expanded based on specific needs
	return strings.ReplaceAll(input, "<", "&lt;")
}