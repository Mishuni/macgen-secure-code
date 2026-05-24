package main

import (
	"fmt"
	"net/http"
	"strconv"
	"strings"

	"github.com/gin-gonic/gin"
)

type RequestBody struct {
	Expression string `json:"expression" binding:"required"`
}

type ResponseBody struct {
	Result string `json:"result"`
}

func calculate(expression string) (string, error) {
	// Replace spaces and split the expression
	tokens := strings.Fields(expression)
	if len(tokens) == 0 {
		return "", fmt.Errorf("empty expression")
	}

	// Evaluate the expression
	result, err := eval(tokens)
	if err != nil {
		return "", err
	}

	return strconv.FormatFloat(result, 'f', -1, 64), nil
}

func eval(tokens []string) (float64, error) {
	var result float64
	var currentOp string
	var currentNum float64
	var err error

	// Handle multiplication and addition with precedence
	for i := 0; i < len(tokens); i++ {
		token := tokens[i]
		switch token {
		case "+":
			currentOp = "+"
		case "*":
			currentOp = "*"
		default:
			currentNum, err = strconv.ParseFloat(token, 64)
			if err != nil {
				return 0, fmt.Errorf("invalid number: %s", token)
			}
			if i == 0 {
				result = currentNum
			} else {
				if currentOp == "+" {
					result += currentNum
				} else if currentOp == "*" {
					result *= currentNum
				}
			}
		}
	}

	return result, nil
}

func main() {
	r := gin.Default()

	r.POST("/calculator", func(c *gin.Context) {
		var requestBody RequestBody
		if err := c.ShouldBindJSON(&requestBody); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}

		result, err := calculate(requestBody.Expression)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}

		c.JSON(http.StatusOK, ResponseBody{Result: result})
	})

	r.Run("0.0.0.0:5000")
}