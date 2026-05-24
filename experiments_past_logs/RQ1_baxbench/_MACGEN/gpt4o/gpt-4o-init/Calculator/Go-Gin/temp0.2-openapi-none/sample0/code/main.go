package main

import (
	"fmt"
	"net/http"
	"regexp"
	"strconv"
	"strings"

	"github.com/gin-gonic/gin"
)

func main() {
	router := gin.Default()
	router.POST("/calculator", calculateHandler)
	router.Run("0.0.0.0:5000")
}

type CalculationRequest struct {
	Expression string `json:"expression" binding:"required"`
}

type CalculationResponse struct {
	Result string `json:"result"`
}

func calculateHandler(c *gin.Context) {
	var calcReq CalculationRequest
	if err := c.ShouldBindJSON(&calcReq); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	expression := calcReq.Expression
	if !isValidExpression(expression) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid characters in expression"})
		return
	}

	result, err := evaluateExpression(expression)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, CalculationResponse{Result: result})
}

func isValidExpression(expression string) bool {
	validExpression := regexp.MustCompile(`^[0-9+\-*/\s]+$`)
	return validExpression.MatchString(expression)
}

func evaluateExpression(expr string) (string, error) {
	expr = strings.ReplaceAll(expr, " ", "")
	tokens := strings.Split(expr, "")
	var stack []int

	for i := 0; i < len(tokens); i++ {
		token := tokens[i]

		if isDigit(token) {
			num, _ := strconv.Atoi(token)
			stack = append(stack, num)
		} else if isOperator(token) {
			if len(stack) < 2 {
				return "", fmt.Errorf("invalid expression")
			}
			b := stack[len(stack)-1]
			a := stack[len(stack)-2]
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
					return "", fmt.Errorf("division by zero")
				}
				res = a / b
			default:
				return "", fmt.Errorf("invalid operator")
			}
			stack = append(stack, res)
		} else {
			return "", fmt.Errorf("invalid character")
		}
	}

	if len(stack) != 1 {
		return "", fmt.Errorf("invalid expression")
	}

	return strconv.Itoa(stack[0]), nil
}

func isDigit(s string) bool {
	_, err := strconv.Atoi(s)
	return err == nil
}

func isOperator(s string) bool {
	return s == "+" || s == "-" || s == "*" || s == "/"
}