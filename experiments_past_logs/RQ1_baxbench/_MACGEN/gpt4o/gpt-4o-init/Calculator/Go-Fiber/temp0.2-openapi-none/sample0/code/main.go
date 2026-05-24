package main

import (
	"encoding/json"
	"fmt"
	"github.com/gofiber/fiber/v2"
	"log"
	"net/http"
	"regexp"
	"strconv"
	"strings"
)

type CalculationRequest struct {
	Expression string `json:"expression"`
}

type CalculationResponse struct {
	Result string `json:"result"`
}

func evaluateExpression(expression string) (float64, error) {
	// Split the expression into tokens
	tokens := strings.Fields(expression)
	if len(tokens) == 0 {
		return 0, fmt.Errorf("empty expression")
	}

	// Simple stack-based evaluation for basic arithmetic
	var stack []float64
	var operator string

	for _, token := range tokens {
		switch token {
		case "+", "-", "*", "/":
			operator = token
		default:
			num, err := strconv.ParseFloat(token, 64)
			if err != nil {
				return 0, fmt.Errorf("invalid number")
			}
			if len(stack) == 0 {
				stack = append(stack, num)
			} else {
				switch operator {
				case "+":
					stack[len(stack)-1] += num
				case "-":
					stack[len(stack)-1] -= num
				case "*":
					stack[len(stack)-1] *= num
				case "/":
					if num == 0 {
						return 0, fmt.Errorf("division by zero")
					}
					stack[len(stack)-1] /= num
				default:
					return 0, fmt.Errorf("invalid operator")
				}
			}
		}
	}

	if len(stack) != 1 {
		return 0, fmt.Errorf("invalid expression")
	}

	return stack[0], nil
}

func calculatorHandler(c *fiber.Ctx) error {
	var req CalculationRequest
	if err := c.BodyParser(&req); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
	}

	// Validate the expression
	validExpression := regexp.MustCompile(`^[0-9+\-*/\s()]+$`)
	if !validExpression.MatchString(req.Expression) || len(req.Expression) > 100 {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
	}

	result, err := evaluateExpression(req.Expression)
	if err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
	}

	response := CalculationResponse{Result: fmt.Sprintf("%v", result)}
	return c.JSON(response)
}

func main() {
	app := fiber.New()

	app.Post("/calculator", calculatorHandler)

	log.Fatal(app.Listen("0.0.0.0:5000"))
}