package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"github.com/gofiber/fiber/v2"
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

func main() {
	app := fiber.New()

	// POST /calculator endpoint
	app.Post("/calculator", func(c *fiber.Ctx) error {
		// Parse and validate the request body
		var req CalculationRequest
		if err := c.BodyParser(&req); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "Invalid request body",
			})
		}

		// Sanitize and validate the expression
		expression := strings.TrimSpace(req.Expression)
		if expression == "" {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "Expression cannot be empty",
			})
		}

		// Validate the expression using a regex to allow only numbers, operators, and spaces
		validExpression := regexp.MustCompile(`^[0-9+\-*/().\s]+$`)
		if !validExpression.MatchString(expression) {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "Invalid characters in expression",
			})
		}

		// Evaluate the expression
		result, err := evaluateExpression(expression)
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "Invalid arithmetic expression",
			})
		}

		// Return the result
		return c.JSON(CalculationResponse{
			Result: fmt.Sprintf("%g", result),
		})
	})

	// Start the server on 0.0.0.0:5000
	app.Listen("0.0.0.0:5000")
}

// evaluateExpression safely evaluates a mathematical expression
func evaluateExpression(expression string) (float64, error) {
	// Tokenize the expression
	tokens := strings.Fields(expression)

	// Convert infix to postfix (Reverse Polish Notation)
	postfix, err := infixToPostfix(tokens)
	if err != nil {
		return 0, err
	}

	// Evaluate the postfix expression
	return evaluatePostfix(postfix)
}

// infixToPostfix converts an infix expression to postfix (RPN)
func infixToPostfix(tokens []string) ([]string, error) {
	var postfix []string
	var stack []string

	precedence := map[string]int{
		"+": 1,
		"-": 1,
		"*": 2,
		"/": 2,
	}

	isOperator := func(token string) bool {
		_, exists := precedence[token]
		return exists
	}

	for _, token := range tokens {
		if isOperator(token) {
			for len(stack) > 0 && precedence[stack[len(stack)-1]] >= precedence[token] {
				postfix = append(postfix, stack[len(stack)-1])
				stack = stack[:len(stack)-1]
			}
			stack = append(stack, token)
		} else if token == "(" {
			stack = append(stack, token)
		} else if token == ")" {
			for len(stack) > 0 && stack[len(stack)-1] != "(" {
				postfix = append(postfix, stack[len(stack)-1])
				stack = stack[:len(stack)-1]
			}
			if len(stack) == 0 || stack[len(stack)-1] != "(" {
				return nil, errors.New("mismatched parentheses")
			}
			stack = stack[:len(stack)-1]
		} else {
			// Assume token is a number
			if _, err := strconv.ParseFloat(token, 64); err != nil {
				return nil, errors.New("invalid number in expression")
			}
			postfix = append(postfix, token)
		}
	}

	for len(stack) > 0 {
		if stack[len(stack)-1] == "(" {
			return nil, errors.New("mismatched parentheses")
		}
		postfix = append(postfix, stack[len(stack)-1])
		stack = stack[:len(stack)-1]
	}

	return postfix, nil
}

// evaluatePostfix evaluates a postfix (RPN) expression
func evaluatePostfix(postfix []string) (float64, error) {
	var stack []float64

	for _, token := range postfix {
		if num, err := strconv.ParseFloat(token, 64); err == nil {
			stack = append(stack, num)
		} else {
			if len(stack) < 2 {
				return 0, errors.New("invalid postfix expression")
			}
			b := stack[len(stack)-1]
			a := stack[len(stack)-2]
			stack = stack[:len(stack)-2]

			switch token {
			case "+":
				stack = append(stack, a+b)
			case "-":
				stack = append(stack, a-b)
			case "*":
				stack = append(stack, a*b)
			case "/":
				if b == 0 {
					return 0, errors.New("division by zero")
				}
				stack = append(stack, a/b)
			default:
				return 0, errors.New("invalid operator in expression")
			}
		}
	}

	if len(stack) != 1 {
		return 0, errors.New("invalid postfix expression")
	}

	return stack[0], nil
}