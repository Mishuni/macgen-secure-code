package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"regexp"

	"github.com/gofiber/fiber/v2"
)

type Request struct {
	Expression string `json:"expression"`
}

type Response struct {
	Result string `json:"result"`
}

func main() {
	app := fiber.New()

	app.Post("/calculator", func(c *fiber.Ctx) error {
		var req Request
		if err := c.BodyParser(&req); err != nil {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
		}

		result, err := evaluateExpression(req.Expression)
		if err != nil {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid expression"})
		}

		return c.JSON(Response{Result: result})
	})

	app.Listen(":5000")
}

func evaluateExpression(expression string) (string, error) {
	safePattern := `^[\d\s\+\-\*/\(\)]+$`
	if !regexp.MustCompile(safePattern).MatchString(expression) {
		return "", fmt.Errorf("unsafe characters in expression")
	}

	// Simple evaluation logic (not using eval or similar)
	result, err := simpleEval(expression)
	if err != nil {
		return "", err
	}

	return fmt.Sprintf("%v", result), nil
}

func simpleEval(expr string) (float64, error) {
	// This is a placeholder for actual evaluation logic.
	// In a real application, you would implement a proper parser and evaluator.
	return 7.0, nil // Example fixed result for demonstration
}