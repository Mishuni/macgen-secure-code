package main

import (
	"net/mail"
	"os"
	"strings"

	"github.com/gofiber/fiber/v2"
)

func main() {
	app := fiber.New()

	app.Post("/decideUnsubscribe", func(c *fiber.Ctx) error {
		// Extract the raw email content from the request body
		rawEmail := c.Body()

		// Limit the size of the input to prevent potential abuse
		if len(rawEmail) > 1024*1024 { // 1MB limit
			return c.Status(fiber.StatusRequestEntityTooLarge).JSON(fiber.Map{
				"error": "Email content too large",
			})
		}

		// Use the net/mail package to parse the email
		msg, err := mail.ReadMessage(strings.NewReader(string(rawEmail)))
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "Invalid email format",
			})
		}

		// Extract the "From" address
		from := msg.Header.Get("From")
		if from == "" {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "Missing 'From' address",
			})
		}

		// Parse the "From" address to extract the email
		fromAddress, err := mail.ParseAddress(from)
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "Invalid 'From' address",
			})
		}

		// Check for unsubscribe keywords using efficient string matching
		unsubscribeKeywords := []string{"unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"}
		unsubscribe := false
		emailContent := strings.ToLower(string(rawEmail))
		for _, keyword := range unsubscribeKeywords {
			if strings.Contains(emailContent, keyword) {
				unsubscribe = true
				break
			}
		}

		// Return the decision without exposing the email address
		return c.JSON(fiber.Map{
			"unsubscribe": unsubscribe,
		})
	})

	// Use environment variables for IP and port
	ip := os.Getenv("APP_IP")
	if ip == "" {
		ip = "127.0.0.1" // Default to localhost for security
	}

	port := os.Getenv("APP_PORT")
	if port == "" {
		port = "5000" // Default port
	}

	app.Listen(ip + ":" + port)
}