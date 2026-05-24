package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strconv"
	"strings"

	"github.com/gofiber/fiber/v2"
)

type Request struct {
	Expression string `json:"expression"`
}

type Response struct {
	Result string `json:"result"`
}

func calculate(expression string) (string, error) {
	tokens := tokenize(expression)
	if len(tokens) == 0 {
		return "", fmt.Errorf("invalid input")
	}

	result, err := eval(tokens)
	if err != nil {
		return "", err
	}

	return strconv.FormatFloat(result, 'f', -1, 64), nil
}

func tokenize(expression string) []string {
	var tokens []string
	var currentToken strings.Builder

	for _, char := range expression {
		if isOperator(string(char)) || char == ' ' {
			if currentToken.Len() > 0 {
				tokens = append(tokens, currentToken.String())
				currentToken.Reset()
			}
			if isOperator(string(char)) {
				tokens = append(tokens, string(char))
			}
		} else {
			currentToken.WriteRune(char)
		}
	}
	if currentToken.Len() > 0 {
		tokens = append(tokens, currentToken.String())
	}

	return tokens
}

func eval(tokens []string) (float64, error) {
	var output []float64
	var operators []string

	for _, token := range tokens {
		if isOperator(token) {
			for len(operators) > 0 && precedence(operators[len(operators)-1]) >= precedence(token) {
				output = append(output, applyOperator(&output, &operators))
			}
			operators = append(operators, token)
		} else {
			num, err := strconv.ParseFloat(token, 64)
			if err != nil {
				return 0, fmt.Errorf("invalid number: %s", token)
			}
			output = append(output, num)
		}
	}

	for len(operators) > 0 {
		output = append(output, applyOperator(&output, &operators))
	}

	if len(output) == 0 {
		return 0, fmt.Errorf("no result")
	}
	return output[0], nil
}

func isOperator(token string) bool {
	return token == "+" || token == "-" || token == "*" || token == "/"
}

func precedence(operator string) int {
	switch operator {
	case "+", "-":
		return 1
	case "*", "/":
		return 2
	default:
		return 0
	}
}

func applyOperator(output *[]float64, operators *[]string) float64 {
	if len(*output) < 2 {
		return 0 // Not enough operands
	}
	b := (*output)[len(*output)-1]
	a := (*output)[len(*output)-2]
	*output = (*output)[:len(*output)-2]
	operator := (*operators)[len(*operators)-1]
	*operators = (*operators)[:len(*operators)-1]

	switch operator {
	case "+":
		return a + b
	case "-":
		return a - b
	case "*":
		return a * b
	case "/":
		if b == 0 {
			return 0 // Handle division by zero
		}
		return a / b
	default:
		return 0
	}
}

func main() {
	app := fiber.New()

	app.Post("/calculator", func(c *fiber.Ctx) error {
		var req Request
		if err := c.BodyParser(&req); err != nil {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
		}

		result, err := calculate(req.Expression)
		if err != nil {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": err.Error()})
		}

		return c.JSON(Response{Result: result})
	})

	app.Listen(":5000")
}