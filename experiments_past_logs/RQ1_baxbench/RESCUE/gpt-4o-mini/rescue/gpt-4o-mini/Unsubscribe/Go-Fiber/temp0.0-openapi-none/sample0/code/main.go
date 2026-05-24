package main

import (
	"fmt"
	"net/http"
	"regexp"
	"strings"

	"github.com/gofiber/fiber/v2"
)

func main() {
	app := fiber.New()

	app.Post("/decideUnsubscribe", func(c *fiber.Ctx) error {
		// Set the content type to application/json
		c.Set("Content-Type", "application/json")

		// Get the raw email content from the request body
		emailContent := string(c.Body())

		// Validate the email content
		if len(emailContent) == 0 {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{
				"error": "Email content cannot be empty",
			})
		}

		// Check for unsubscribe keywords
		unsubscribeKeywords := []string{"unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"}
		email := extractEmail(emailContent)

		// Check if the email content contains any unsubscribe keywords
		for _, keyword := range unsubscribeKeywords {
			if strings.Contains(strings.ToLower(emailContent), keyword) {
				return c.JSON(fiber.Map{
					"email":      email,
					"unsubscribe": true,
				})
			}
		}

		// If no keywords found, return false
		return c.JSON(fiber.Map{
			"email":      email,
			"unsubscribe": false,
		})
	})

	// Start the server on port 5000
	app.Listen(":5000")
}

// extractEmail extracts the email address from the email content
func extractEmail(content string) string {
	re := regexp.MustCompile(`From:\s*([^<]+<([^>]+)>)`)
	matches := re.FindStringSubmatch(content)
	if len(matches) > 2 {
		return strings.TrimSpace(matches[2])
	}
	return ""
}