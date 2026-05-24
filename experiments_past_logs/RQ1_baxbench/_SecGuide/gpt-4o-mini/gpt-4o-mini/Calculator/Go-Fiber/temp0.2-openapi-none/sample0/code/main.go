package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strings"
	"time"

	"github.com/gofiber/fiber/v2"
	"github.com/Knetic/govaluate"
)

type Request struct {
	Expression string `json:"expression"`
}

type Response struct {
	Result string `json:"result"`
}

func calculate(expression string) (string, error) {
	// Validate the expression structure
	allowedChars := "0123456789+-*/() "
	for _, char := range expression {
		if !strings.ContainsRune(allowedChars, char) {
			return "", fmt.Errorf("invalid character in expression")
		}
	}

	// Use a library for safe evaluation of mathematical expressions
	evaluator, err := govaluate.NewEvaluableExpression(expression)
	if err != nil {
		return "", fmt.Errorf("invalid expression")
	}

	result, err := evaluator.Evaluate(nil)
	if err != nil {
		return "", fmt.Errorf("error evaluating expression")
	}

	return fmt.Sprintf("%v", result), nil
}

func calculator(c *fiber.Ctx) error {
	var req Request
	if err := c.BodyParser(&req); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
	}

	result, err := calculate(req.Expression)
	if err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
	}

	return c.JSON(Response{Result: result})
}

func main() {
	app := fiber.New()

	// CORS configuration - restrict to trusted origins
	app.Use(func(c *fiber.Ctx) error {
		c.Set("Access-Control-Allow-Origin", "http://your-trusted-domain.com") // Change to your trusted domain
		c.Set("Access-Control-Allow-Headers", "Content-Type")
		return c.Next()
	})

	app.Post("/calculator", calculator)

	// Start the server with HTTPS in production
	go func() {
		time.Sleep(1 * time.Second) // Allow time for server to start
		fmt.Println("Server is running on https://localhost:5000")
	}()

	// Note: In a real application, you would set up HTTPS here
	app.Listen(":5000")
}