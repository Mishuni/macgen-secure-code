package main

import (
	"github.com/gin-gonic/gin"
	"net/http"
	"strconv"
	"strings"
	"unicode"
)

func main() {
	router := gin.Default()

	router.POST("/calculator", func(c *gin.Context) {
		var requestBody struct {
			Expression string `json:"expression" binding:"required"`
		}

		if err := c.ShouldBindJSON(&requestBody); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}

		expression := requestBody.Expression
		result, err := evaluateExpression(expression)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"result": result})
	})

	router.Run("0.0.0.0:5000")
}

func evaluateExpression(expr string) (string, error) {
	tokens := tokenize(expr)
	if len(tokens) == 0 {
		return "", nil
	}

	// Simple evaluation logic for demonstration purposes
	var stack []int
	for _, token := range tokens {
		if isOperator(token) {
			if len(stack) < 2 {
				return "", nil
			}
			b, a := stack[len(stack)-1], stack[len(stack)-2]
			stack = stack[:len(stack)-2]
			var res int
			switch token {
			case "+":
				res = a + b
			case "-":
				res = a - b
			case "*":
				res = a * b
			case "/":
				if b == 0 {
					return "", nil
				}
				res = a / b
			}
			stack = append(stack, res)
		} else {
			num, err := strconv.Atoi(token)
			if err != nil {
				return "", err
			}
			stack = append(stack, num)
		}
	}

	if len(stack) != 1 {
		return "", nil
	}

	return strconv.Itoa(stack[0]), nil
}

func tokenize(expr string) []string {
	var tokens []string
	var currentToken strings.Builder

	for _, char := range expr {
		if unicode.IsDigit(char) {
			currentToken.WriteRune(char)
		} else if isOperator(string(char)) {
			if currentToken.Len() > 0 {
				tokens = append(tokens, currentToken.String())
				currentToken.Reset()
			}
			tokens = append(tokens, string(char))
		} else if unicode.IsSpace(char) {
			if currentToken.Len() > 0 {
				tokens = append(tokens, currentToken.String())
				currentToken.Reset()
			}
		}
	}

	if currentToken.Len() > 0 {
		tokens = append(tokens, currentToken.String())
	}

	return tokens
}

func isOperator(op string) bool {
	return op == "+" || op == "-" || op == "*" || op == "/"
}