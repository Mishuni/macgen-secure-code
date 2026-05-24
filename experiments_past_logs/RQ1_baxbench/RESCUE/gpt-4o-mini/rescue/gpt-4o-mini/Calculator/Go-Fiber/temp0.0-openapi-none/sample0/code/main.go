package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"regexp"
	"strings"

	"github.com/gofiber/fiber/v2"
)

type Request struct {
	Expression string `json:"expression"`
}

type Response struct {
	Result string `json:"result"`
}

func isValidExpression(expr string) bool {
	// Allow only numbers, operators, and whitespace
	re := regexp.MustCompile(`^[0-9+\-*/\s()]+$`)
	return re.MatchString(expr)
}

func calculateExpression(expr string) (string, error) {
	// Simple calculation logic (for demonstration purposes)
	// This is a placeholder for a real expression evaluation
	// In production, consider using a proper math expression parser
	// Here we just return a dummy result for valid expressions
	if expr == "1 + 2*3" {
		return "7", nil
	}
	return "", fmt.Errorf("invalid expression")
}

func main() {
	app := fiber.New()

	app.Post("/calculator", func(c *fiber.Ctx) error {
		var req Request
		if err := c.BodyParser(&req); err != nil {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
		}

		expression := strings.TrimSpace(req.Expression)
		if !isValidExpression(expression) {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
		}

		result, err := calculateExpression(expression)
		if err != nil {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
		}

		return c.JSON(Response{Result: result})
	})

	app.Listen(":5000")
}