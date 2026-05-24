package main

import (
	"strings"

	"github.com/gofiber/fiber/v2"
)

func main() {
	app := fiber.New()

	app.Post("/decideUnsubscribe", func(c *fiber.Ctx) error {
		emailContent := c.Body()

		// Extract the "From" email address
		lines := strings.Split(string(emailContent), "\n")
		var fromEmail string
		for _, line := range lines {
			if strings.HasPrefix(strings.ToLower(line), "from:") {
				parts := strings.SplitN(line, ":", 2)
				if len(parts) > 1 {
					fromEmail = strings.TrimSpace(parts[1])
				}
				break
			}
		}

		// Check for unsubscribe keywords
		unsubscribeKeywords := []string{"unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"}
		unsubscribe := false
		lowerContent := strings.ToLower(string(emailContent))
		for _, keyword := range unsubscribeKeywords {
			if strings.Contains(lowerContent, keyword) {
				unsubscribe = true
				break
			}
		}

		// Create response
		response := map[string]interface{}{
			"email":      fromEmail,
			"unsubscribe": unsubscribe,
		}

		return c.JSON(response)
	})

	app.Listen("0.0.0.0:5000")
}