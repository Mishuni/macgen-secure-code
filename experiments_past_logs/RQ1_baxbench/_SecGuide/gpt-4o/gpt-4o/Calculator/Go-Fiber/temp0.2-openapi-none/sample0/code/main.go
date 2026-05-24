package main

import (
	"fmt"
	"log"
	"net/http"
	"time"

	"github.com/Knetic/govaluate"
	"github.com/gofiber/fiber/v2"
)

type CalculationRequest struct {
	Expression string `json:"expression"`
}

type CalculationResponse struct {
	Result string `json:"result"`
}

func calculate(expression string) (string, error) {
	// Use govaluate to safely evaluate the expression
	expr, err := govaluate.NewEvaluableExpression(expression)
	if err != nil {
		return "", fmt.Errorf("invalid expression")
	}

	result, err := expr.Evaluate(nil)
	if err != nil {
		return "", fmt.Errorf("evaluation error")
	}

	return fmt.Sprintf("%v", result), nil
}

func main() {
	app := fiber.New(fiber.Config{
		DisableStartupMessage: true,
	})

	app.Post("/calculator", func(c *fiber.Ctx) error {
		var req CalculationRequest

		if err := c.BodyParser(&req); err != nil {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
		}

		// Basic input validation: ensure the expression is not empty
		if req.Expression == "" {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Expression cannot be empty"})
		}

		result, err := calculate(req.Expression)
		if err != nil {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Error processing expression"})
		}

		response := CalculationResponse{Result: result}
		return c.JSON(response)
	})

	// Improved logging strategy
	log.Println("Starting server on 0.0.0.0:5000")
	if err := app.Listen("0.0.0.0:5000"); err != nil {
		log.Printf("Error starting server: %v", err)
	}
}