package main

import (
	"github.com/gofiber/fiber/v2"
	"go/token"
	"go/types"
	"strconv"
	"strings"
)

func main() {
	app := fiber.New()

	app.Post("/calculator", func(c *fiber.Ctx) error {
		var request struct {
			Expression string `json:"expression"`
		}

		if err := c.BodyParser(&request); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "Invalid input",
			})
		}

		// Sanitize input to prevent potential code injection
		expression := sanitizeExpression(request.Expression)

		result, err := evaluateExpression(expression)
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "Invalid input",
			})
		}

		return c.JSON(fiber.Map{
			"result": result,
		})
	})

	app.Listen("0.0.0.0:5000")
}

func sanitizeExpression(expr string) string {
	// Allow only numbers, operators, and parentheses
	allowedChars := "0123456789+-*/(). "
	var sanitized strings.Builder
	for _, char := range expr {
		if strings.ContainsRune(allowedChars, char) {
			sanitized.WriteRune(char)
		}
	}
	return sanitized.String()
}

func evaluateExpression(expr string) (string, error) {
	// Use Go's types.Eval to safely evaluate the expression
	fs := token.NewFileSet()
	tv, err := types.Eval(fs, nil, token.NoPos, expr)
	if err != nil {
		return "", err
	}

	// Convert the result to a string
	return strconv.FormatFloat(tv.Value.Float(), 'f', -1, 64), nil
}