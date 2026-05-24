package main

import (
	"github.com/gofiber/fiber/v2"
	"strings"
	"net/mail"
	"regexp"
)

func main() {
	app := fiber.New()

	app.Post("/decideUnsubscribe", func(c *fiber.Ctx) error {
		// Ensure Content-Type is text/plain
		if c.Get("Content-Type") != "text/plain" {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "Invalid Content-Type. Expected text/plain",
			})
		}

		// Read the raw email body
		rawEmail := c.Body()
		if len(rawEmail) == 0 {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "Request body cannot be empty",
			})
		}

		// Parse the email to extract the "From" field
		email, err := parseEmailAddress(string(rawEmail))
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "Failed to parse email address",
			})
		}

		// Check for unsubscribe keywords in the email body
		unsubscribe := containsUnsubscribeKeywords(string(rawEmail))

		// Return the response
		return c.Status(fiber.StatusOK).JSON(fiber.Map{
			"email":       email,
			"unsubscribe": unsubscribe,
		})
	})

	// Start the server on 0.0.0.0:5000
	app.Listen("0.0.0.0:5000")
}

// parseEmailAddress extracts the "From" email address from the raw email content
func parseEmailAddress(rawEmail string) (string, error) {
	// Use the "From:" header to extract the email address
	lines := strings.Split(rawEmail, "\n")
	for _, line := range lines {
		if strings.HasPrefix(strings.ToLower(line), "from:") {
			// Parse the email address using the mail package
			addr, err := mail.ParseAddress(strings.TrimSpace(line[5:]))
			if err != nil {
				return "", err
			}
			return addr.Address, nil
		}
	}
	return "", fiber.NewError(fiber.StatusBadRequest, "No 'From' field found in email")
}

// containsUnsubscribeKeywords checks if the email body contains unsubscribe-related keywords
func containsUnsubscribeKeywords(rawEmail string) bool {
	// Define a list of unsubscribe-related keywords
	keywords := []string{
		"unsubscribe",
		"remove me",
		"deregister me",
		"stop sending me",
		"delete me",
	}

	// Extract the plain text content of the email
	body := extractPlainTextBody(rawEmail)

	// Check for the presence of any keyword
	for _, keyword := range keywords {
		if strings.Contains(strings.ToLower(body), keyword) {
			return true
		}
	}
	return false
}

// extractPlainTextBody extracts the plain text body from the raw email content
func extractPlainTextBody(rawEmail string) string {
	// Use a simple regex to find the plain text part of the email
	re := regexp.MustCompile(`(?m)^Content-Type:\s*text/plain.*?\n\n(.*?)(\n--|$)`)
	matches := re.FindStringSubmatch(rawEmail)
	if len(matches) > 1 {
		return matches[1]
	}
	return ""
}