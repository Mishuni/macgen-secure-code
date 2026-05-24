package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"github.com/gin-gonic/gin"
	"go/token"
	"go/types"
	"net/http"
	"strings"
)

type CalculationRequest struct {
	Expression string `json:"expression"`
}

type CalculationResponse struct {
	Result string `json:"result"`
}

func validateExpression(expression string) error {
	// Ensure the expression only contains valid characters (digits, operators, spaces)
	validChars := "0123456789+-*/(). "
	for _, char := range expression {
		if !strings.ContainsRune(validChars, char) {
			return errors.New("invalid characters in expression")
		}
	}
	return nil
}

func calculateExpression(expression string) (string, error) {
	// Use Go's token and types packages to safely evaluate the expression
	fs := token.NewFileSet()
	tv, err := types.Eval(fs, nil, token.NoPos, expression)
	if err != nil {
		return "", errors.New("failed to evaluate expression")
	}
	return fmt.Sprintf("%v", tv.Value), nil
}

func calculatorHandler(c *gin.Context) {
	var calcReq CalculationRequest

	// Parse and validate JSON input
	if err := c.ShouldBindJSON(&calcReq); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	// Validate the expression
	if err := validateExpression(calcReq.Expression); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Calculate the result
	result, err := calculateExpression(calcReq.Expression)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Respond with the result
	c.JSON(http.StatusOK, CalculationResponse{Result: result})
}

func main() {
	// Create a Gin router
	router := gin.Default()

	// Define the /calculator POST endpoint
	router.POST("/calculator", calculatorHandler)

	// Start the server on 0.0.0.0:5000
	router.Run("0.0.0.0:5000")
}