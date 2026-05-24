package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strings"
	"time"

	"github.com/Knetic/govaluate"
	"github.com/gin-gonic/gin"
)

func main() {
	router := gin.Default()

	// Middleware for logging requests
	router.Use(gin.Logger())

	router.POST("/calculator", func(c *gin.Context) {
		var requestBody struct {
			Expression string `json:"expression"`
		}

		if err := c.ShouldBindJSON(&requestBody); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}

		// Validate the expression
		if !isValidExpression(requestBody.Expression) {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}

		result, err := evaluateExpression(requestBody.Expression)
		if err != nil {
			log.Printf("Error evaluating expression: %v", err)
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"result": result})
	})

	// Run the server with a timeout to prevent DoS
	srv := &http.Server{
		Addr:         "0.0.0.0:5000",
		Handler:      router,
		ReadTimeout:  5 * time.Second,
		WriteTimeout: 10 * time.Second,
	}

	log.Fatal(srv.ListenAndServe())
}

// isValidExpression performs basic validation on the expression
func isValidExpression(expr string) bool {
	// Allow only numbers, basic operators, and parentheses
	for _, char := range expr {
		if !strings.ContainsRune("0123456789+-*/(). ", char) {
			return false
		}
	}
	return true
}

func evaluateExpression(expr string) (interface{}, error) {
	// Use govaluate to safely evaluate the expression
	expression, err := govaluate.NewEvaluableExpression(expr)
	if err != nil {
		return nil, fmt.Errorf("invalid input")
	}

	result, err := expression.Evaluate(nil)
	if err != nil {
		return nil, fmt.Errorf("invalid input")
	}

	return result, nil
}