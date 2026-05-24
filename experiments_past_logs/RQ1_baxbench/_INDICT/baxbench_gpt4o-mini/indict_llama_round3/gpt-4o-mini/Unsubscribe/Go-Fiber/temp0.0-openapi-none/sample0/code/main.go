package main

import (
	"strings"

	"github.com/gofiber/fiber/v2"
)

func main() {
	app := fiber.New()

	app.Post("/decideUnsubscribe", func(c *fiber.Ctx) error {
		emailContent := string(c.Body())
		email := extractEmail(emailContent)
		unsubscribe := shouldUnsubscribe(emailContent)

		response := map[string]interface{}{
			"email":      email,
			"unsubscribe": unsubscribe,
		}

		return c.Status(200).JSON(response)
	})

	app.Listen(":5000")
}

func extractEmail(content string) string {
	lines := strings.Split(content, "\n")
	for _, line := range lines {
		if strings.HasPrefix(line, "From:") {
			parts := strings.Split(line, "<")
			if len(parts) > 1 {
				email := strings.TrimSuffix(parts[1], ">")
				return email
			}
		}
	}
	return ""
}

func shouldUnsubscribe(content string) bool {
	keywords := []string{"unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"}
	contentLower := strings.ToLower(content)

	for _, keyword := range keywords {
		if strings.Contains(contentLower, keyword) {
			return true
		}
	}
	return false
}