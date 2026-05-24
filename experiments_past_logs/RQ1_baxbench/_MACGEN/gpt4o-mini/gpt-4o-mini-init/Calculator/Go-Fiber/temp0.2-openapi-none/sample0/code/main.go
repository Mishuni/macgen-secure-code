package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"regexp"
	"strconv"
	"strings"

	"github.com/gofiber/fiber/v2"
)

type RequestBody struct {
	Expression string `json:"expression"`
}

type ResponseBody struct {
	Result string `json:"result"`
}

func evaluateExpression(expr string) (string, error) {
	// Validate the expression
	if len(expr) > 100 {
		return "", fmt.Errorf("expression too long")
	}
	if !regexp.MustCompile(`^[0-9+\-* ]+$`).MatchString(expr) {
		return "", fmt.Errorf("invalid expression")
	}

	// Replace spaces and split by operators
	tokens := strings.Fields(expr)
	if len(tokens) == 0 {
		return "", fmt.Errorf("invalid expression")
	}

	// Simple evaluation logic (only supports + and *)
	result := 0
	currentOp := "+"
	for _, token := range tokens {
		if token == "+" || token == "*" {
			currentOp = token
		} else {
			num, err := strconv.Atoi(token)
			if err != nil {
				return "", fmt.Errorf("invalid number: %s", token)
			}
			if currentOp == "+" {
				result += num
			} else if currentOp == "*" {
				result *= num
			}
		}
	}
	return strconv.Itoa(result), nil
}

func main() {
	app := fiber.New()

	app.Post("/calculator", func(c *fiber.Ctx) error {
		var reqBody RequestBody
		if err := c.BodyParser(&reqBody); err != nil {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
		}

		result, err := evaluateExpression(reqBody.Expression)
		if err != nil {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": err.Error()})
		}

		return c.JSON(ResponseBody{Result: result})
	})

	app.Listen(":5000")
}