package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"regexp"
	"strconv"
	"strings"

	"github.com/gin-gonic/gin"
)

type Request struct {
	Expression string `json:"expression" binding:"required"`
}

type Response struct {
	Result string `json:"result"`
}

func isValidExpression(expression string) bool {
	// A more robust regex to validate the expression format
	// This allows integers and basic operators (+, -, *, /) with spaces
	re := regexp.MustCompile(`^(\d+\s*[\+\-\*/]\s*)*\d+$`)
	return re.MatchString(expression)
}

func calculate(expression string) (string, error) {
	if !isValidExpression(expression) {
		return "", fmt.Errorf("invalid expression format")
	}

	// Split the expression into parts
	parts := strings.Fields(expression)
	if len(parts) < 3 {
		return "", fmt.Errorf("expression must contain at least one operator and two operands")
	}

	result, err := strconv.Atoi(parts[0])
	if err != nil {
		return "", fmt.Errorf("invalid number: %s", parts[0])
	}

	for i := 1; i < len(parts); i += 2 {
		if i+1 >= len(parts) {
			return "", fmt.Errorf("expression must contain an operator followed by a number")
		}

		operator := parts[i]
		num, err := strconv.Atoi(parts[i+1])
		if err != nil {
			return "", fmt.Errorf("invalid number: %s", parts[i+1])
		}

		switch operator {
		case "+":
			result += num
		case "-":
			result -= num
		case "*":
			result *= num
		case "/":
			if num == 0 {
				return "", fmt.Errorf("division by zero is not allowed")
			}
			result /= num
		default:
			return "", fmt.Errorf("unsupported operator: %s", operator)
		}
	}

	return fmt.Sprintf("%d", result), nil
}

func main() {
	r := gin.Default()

	r.POST("/calculator", func(c *gin.Context) {
		var req Request
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}

		result, err := calculate(req.Expression)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid expression"})
			return
		}

		c.JSON(http.StatusOK, Response{Result: result})
	})

	r.Run("0.0.0.0:5000")
}