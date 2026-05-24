package main

import (
	"net/http"
	"github.com/gin-gonic/gin"
	"regexp"
	"strconv"
	"strings"
)

type RequestBody struct {
	Expression string `json:"expression" binding:"required"`
}

type ResponseBody struct {
	Result string `json:"result"`
}

func main() {
	router := gin.Default()
	router.POST("/calculator", calculate)
	router.Run("0.0.0.0:5000")
}

func calculate(c *gin.Context) {
	var requestBody RequestBody
	if err := c.ShouldBindJSON(&requestBody); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	expression := requestBody.Expression
	if !isValidExpression(expression) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	result, err := evaluateExpression(expression)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Error evaluating expression"})
		return
	}

	c.JSON(http.StatusOK, ResponseBody{Result: result})
}

func isValidExpression(expression string) bool {
	// Allow only digits, operators, and parentheses
	safePattern := `^[\d\s\+\-\*/\(\)]+$`
	return regexp.MustCompile(safePattern).MatchString(expression)
}

func evaluateExpression(expression string) (string, error) {
	// Replace spaces and evaluate the expression
	expression = strings.ReplaceAll(expression, " ", "")
	result, err := eval(expression)
	if err != nil {
		return "", err
	}
	return strconv.FormatFloat(result, 'f', -1, 64), nil
}

// Simple evaluation function for arithmetic expressions
func eval(expr string) (float64, error) {
	// This is a very basic implementation and should be replaced with a proper parser for production use
	var result float64
	var currentNum float64
	var operator byte = '+'

	for i := 0; i < len(expr); i++ {
		ch := expr[i]
		if ch >= '0' && ch <= '9' {
			currentNum = currentNum*10 + float64(ch-'0')
		}
		if ch == '+' || ch == '-' || ch == '*' || ch == '/' || i == len(expr)-1 {
			switch operator {
			case '+':
				result += currentNum
			case '-':
				result -= currentNum
			case '*':
				result *= currentNum
			case '/':
				if currentNum == 0 {
					return 0, http.ErrNotSupported // Handle division by zero
				}
				result /= currentNum
			}
			operator = ch
			currentNum = 0
		}
	}
	return result, nil
}