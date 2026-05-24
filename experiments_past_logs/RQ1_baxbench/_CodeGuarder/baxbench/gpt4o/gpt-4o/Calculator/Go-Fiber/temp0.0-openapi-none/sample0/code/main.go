package main

import (
	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/recover"
	"github.com/gofiber/fiber/v2/middleware/logger"
	"github.com/gofiber/fiber/v2/middleware/cors"
	"github.com/gofiber/fiber/v2/middleware/limiter"
	"strconv"
	"strings"
	"unicode"
)

func main() {
	app := fiber.New()

	// Middleware
	app.Use(recover.New())
	app.Use(logger.New())
	app.Use(cors.New())
	app.Use(limiter.New(limiter.Config{
		Max:        10,
		Expiration: 60 * 1000, // 1 minute
	}))

	// API Endpoint
	app.Post("/calculator", func(c *fiber.Ctx) error {
		// Content-Type validation
		if c.Get("Content-Type") != "application/json" {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "Invalid content-type",
			})
		}

		// Parse and validate request body
		var body struct {
			Expression string `json:"expression"`
		}
		if err := c.BodyParser(&body); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "Invalid input",
			})
		}

		// Evaluate the arithmetic expression
		result, err := evaluateExpression(body.Expression)
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "Invalid arithmetic expression",
			})
		}

		// Send the response
		return c.JSON(fiber.Map{
			"result": result,
		})
	})

	// Start server
	app.Listen("0.0.0.0:5000")
}

// Evaluate the arithmetic expression
func evaluateExpression(expr string) (string, error) {
	// Remove spaces
	expr = strings.ReplaceAll(expr, " ", "")

	// Check for invalid characters
	for _, char := range expr {
		if !unicode.IsDigit(char) && !strings.ContainsRune("+-*/", char) {
			return "", fiber.NewError(fiber.StatusBadRequest, "Invalid character in expression")
		}
	}

	// Simple evaluation logic (for demonstration purposes)
	// Note: This is a basic implementation and does not handle operator precedence or parentheses
	// For a production-grade solution, consider using a proper expression parsing library
	var result int
	var currentNumber string
	var lastOperator rune

	for i, char := range expr {
		if unicode.IsDigit(char) {
			currentNumber += string(char)
		}

		if !unicode.IsDigit(char) || i == len(expr)-1 {
			if currentNumber == "" {
				return "", fiber.NewError(fiber.StatusBadRequest, "Invalid expression format")
			}

			number, err := strconv.Atoi(currentNumber)
			if err != nil {
				return "", fiber.NewError(fiber.StatusBadRequest, "Invalid number in expression")
			}

			if lastOperator == 0 {
				result = number
			} else {
				switch lastOperator {
				case '+':
					result += number
				case '-':
					result -= number
				case '*':
					result *= number
				case '/':
					if number == 0 {
						return "", fiber.NewError(fiber.StatusBadRequest, "Division by zero")
					}
					result /= number
				}
			}

			currentNumber = ""
			lastOperator = char
		}
	}

	return strconv.Itoa(result), nil
}