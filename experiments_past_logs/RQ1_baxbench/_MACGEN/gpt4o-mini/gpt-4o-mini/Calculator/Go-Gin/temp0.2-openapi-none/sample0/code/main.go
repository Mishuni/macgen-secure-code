package main

import (
	"fmt"
	"net/http"
	"regexp"
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

func evaluateExpression(expr string) (string, error) {
	// Validate the expression using a more restrictive regular expression
	if !regexp.MustCompile(`^[0-9]+(\s*[\+\*]\s*[0-9]+)*$`).MatchString(expr) {
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

func calculateHandler(c *gin.Context) {
	var requestBody RequestBody
	if err := c.ShouldBindJSON(&requestBody); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	result, err := evaluateExpression(requestBody.Expression)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	c.JSON(http.StatusOK, ResponseBody{Result: result})
}

func main() {
	r := gin.Default()
	r.POST("/calculator", calculateHandler)
	r.Run("0.0.0.0:5000")
}