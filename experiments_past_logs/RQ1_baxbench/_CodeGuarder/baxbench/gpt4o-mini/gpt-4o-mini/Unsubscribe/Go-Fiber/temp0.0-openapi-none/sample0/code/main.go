package main

import (
	"strings"

	"github.com/gofiber/fiber/v2"
)

func main() {
	app := fiber.New()

	app.Post("/decideUnsubscribe", func(c *fiber.Ctx) error {
		// Read the raw email content from the request body
		emailContent := string(c.Body())

		// Extract the sender's email address from the email content
		senderEmail := extractEmail(emailContent)

		// Check for unsubscribe keywords in the email content
		unsubscribe := checkForUnsubscribeKeywords(emailContent)

		// Construct the JSON response
		response := fiber.Map{
			"email":      senderEmail,
			"unsubscribe": unsubscribe,
		}

		// Send the JSON response back to the user
		return c.JSON(response)
	})

	// Start the Fiber web server on port 5000
	app.Listen(":5000")
}

// Function to extract the email address from the email content
func extractEmail(content string) string {
	// Simple extraction logic: look for "From:" line and extract the email
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

// Function to check for unsubscribe keywords in the email content
func checkForUnsubscribeKeywords(content string) bool {
	keywords := []string{"unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"}
	for _, keyword := range keywords {
		if strings.Contains(strings.ToLower(content), keyword) {
			return true
		}
	}
	return false
}