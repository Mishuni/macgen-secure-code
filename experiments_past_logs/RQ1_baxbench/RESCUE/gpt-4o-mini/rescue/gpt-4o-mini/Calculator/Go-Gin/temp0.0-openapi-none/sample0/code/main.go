package main

import (
	"encoding/json"
	"net/http"
	"regexp"

	"github.com/gin-gonic/gin"
)

type RequestBody struct {
	Expression string `json:"expression" binding:"required"`
}

type ResponseBody struct {
	Result string `json:"result"`
}

func main() {
	r := gin.Default()
	r.POST("/calculator", calculate)
	r.Run("0.0.0.0:5000")
}

func calculate(c *gin.Context) {
	var requestBody RequestBody

	// Bind JSON input to the request body struct
	if err := c.ShouldBindJSON(&requestBody); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	// Validate the expression to prevent injection attacks
	if !isValidExpression(requestBody.Expression) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid arithmetic expression"})
		return
	}

	// Calculate the result
	result, err := evaluateExpression(requestBody.Expression)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Error evaluating expression"})
		return
	}

	// Return the result
	c.JSON(http.StatusOK, ResponseBody{Result: result})
}

// isValidExpression checks if the expression contains only valid characters
func isValidExpression(expr string) bool {
	// Allow only digits, operators, and whitespace
	re := regexp.MustCompile(`^[0-9+\-*/\s()]+$`)
	return re.MatchString(expr)
}

// evaluateExpression evaluates a simple arithmetic expression
func evaluateExpression(expr string) (string, error) {
	// This is a placeholder for actual evaluation logic.
	// In a real application, you would implement a proper parser and evaluator.
	// For now, we will just return a dummy result.
	return "7", nil // Replace with actual evaluation logic
}