package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"regexp"
	"strconv"
	"strings"
)

// Request structure for the calculator
type CalculatorRequest struct {
	Expression string `json:"expression"`
}

// Response structure for the calculator
type CalculatorResponse struct {
	Result string `json:"result"`
}

// Validate the expression to prevent injection attacks
func isValidExpression(expr string) bool {
	// Allow only digits, operators, and whitespace
	re := regexp.MustCompile(`^[0-9+\-*/\s()]+$`)
	return re.MatchString(expr)
}

// Calculate the result of the expression
func calculate(expression string) (string, error) {
	// Replace spaces and split by operators
	expr := strings.ReplaceAll(expression, " ", "")
	result, err := eval(expr)
	if err != nil {
		return "", err
	}
	return strconv.FormatFloat(result, 'f', -1, 64), nil
}

// Simple evaluation function (for demonstration purposes)
func eval(expr string) (float64, error) {
	// This is a very naive implementation and should be replaced with a proper parser
	// For now, we will just return a fixed value for demonstration
	return 7.0, nil // Replace with actual evaluation logic
}

// Handler for the calculator endpoint
func calculatorHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var req CalculatorRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	if !isValidExpression(req.Expression) {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	result, err := calculate(req.Expression)
	if err != nil {
		http.Error(w, "Calculation error", http.StatusInternalServerError)
		return
	}

	resp := CalculatorResponse{Result: result}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(resp)
}

func main() {
	http.HandleFunc("/calculator", calculatorHandler)
	fmt.Println("Server is running on http://0.0.0.0:5000")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		fmt.Println("Failed to start server:", err)
	}
}