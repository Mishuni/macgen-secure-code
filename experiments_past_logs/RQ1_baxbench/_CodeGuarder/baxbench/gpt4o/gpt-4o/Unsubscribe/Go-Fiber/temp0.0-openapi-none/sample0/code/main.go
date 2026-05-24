package main

import (
	"strings"

	"github.com/gofiber/fiber/v2"
)

func main() {
	app := fiber.New()

	app.Post("/decideUnsubscribe", func(c *fiber.Ctx) error {
		// Validate Content-Type
		if c.Get("Content-Type") != "text/plain" {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "Invalid Content-Type",
			})
		}

		// Parse the incoming request body
		body := c.Body()

		// Extract email address and content
		email, content, err := extractEmailAndContent(string(body))
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "Invalid email format",
			})
		}

		// Analyze email content for unsubscribe keywords
		unsubscribe := analyzeContentForUnsubscribe(content)

		// Construct and send the response
		return c.JSON(fiber.Map{
			"email":       email,
			"unsubscribe": unsubscribe,
		})
	})

	app.Listen("0.0.0.0:5000")
}

// extractEmailAndContent extracts the email address and the main content from the raw email
func extractEmailAndContent(rawEmail string) (string, string, error) {
	lines := strings.Split(rawEmail, "\n")
	var email, content string
	for _, line := range lines {
		if strings.HasPrefix(line, "From:") {
			parts := strings.Split(line, "<")
			if len(parts) > 1 {
				email = strings.TrimSuffix(parts[1], ">")
			}
		}
		if strings.HasPrefix(line, "Content-Type:text/plain") {
			contentStart := strings.Index(rawEmail, line) + len(line)
			content = rawEmail[contentStart:]
			break
		}
	}
	if email == "" || content == "" {
		return "", "", fiber.ErrBadRequest
	}
	return email, content, nil
}

// analyzeContentForUnsubscribe checks if the content contains unsubscribe keywords
func analyzeContentForUnsubscribe(content string) bool {
	unsubscribeKeywords := []string{
		"unsubscribe", "remove me", "deregister me", "stop sending me", "delete me",
	}
	content = strings.ToLower(content)
	for _, keyword := range unsubscribeKeywords {
		if strings.Contains(content, keyword) {
			return true
		}
	}
	return false
}