package main

import (
	"regexp"
	"strings"

	"github.com/gofiber/fiber/v2"
)

func main() {
	app := fiber.New()

	app.Post("/decideUnsubscribe", func(c *fiber.Ctx) error {
		rawEmail := c.Body()

		email, unsubscribe := processEmail(string(rawEmail))

		response := map[string]interface{}{
			"email":      email,
			"unsubscribe": unsubscribe,
		}

		return c.JSON(response)
	})

	app.Listen("0.0.0.0:5000")
}

func processEmail(rawEmail string) (string, bool) {
	lines := strings.Split(rawEmail, "\n")
	var email string
	unsubscribe := false

	for _, line := range lines {
		if strings.HasPrefix(line, "From:") {
			email = extractEmail(line)
		}
		if containsUnsubscribeKeywords(line) {
			unsubscribe = true
		}
	}

	return email, unsubscribe
}

func extractEmail(fromLine string) string {
	re := regexp.MustCompile(`<([^>]+)>`)
	matches := re.FindStringSubmatch(fromLine)
	if len(matches) > 1 {
		return matches[1]
	}
	return ""
}

func containsUnsubscribeKeywords(text string) bool {
	keywords := []string{"unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"}
	text = strings.ToLower(text)
	for _, keyword := range keywords {
		if strings.Contains(text, keyword) {
			return true
		}
	}
	return false
}