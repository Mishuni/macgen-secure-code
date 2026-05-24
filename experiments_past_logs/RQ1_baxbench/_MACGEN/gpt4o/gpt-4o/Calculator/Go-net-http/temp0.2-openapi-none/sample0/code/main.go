package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"regexp"
	"strconv"
	"strings"
	"time"
)

type CalculationRequest struct {
	Expression string `json:"expression"`
}

type CalculationResponse struct {
	Result string `json:"result"`
}

func calculate(expression string) (string, error) {
	// Simple parser for basic arithmetic expressions
	// This is a naive implementation and does not handle operator precedence or parentheses
	tokens := strings.Fields(expression)
	if len(tokens) < 3 {
		return "", fmt.Errorf("invalid expression")
	}

	// Start with the first number
	result, err := strconv.Atoi(tokens[0])
	if err != nil {
		return "", fmt.Errorf("invalid number: %s", tokens[0])
	}

	// Iterate over the tokens
	for i := 1; i < len(tokens)-1; i += 2 {
		operator := tokens[i]
		nextNumber, err := strconv.Atoi(tokens[i+1])
		if err != nil {
			return "", fmt.Errorf("invalid number: %s", tokens[i+1])
		}

		switch operator {
		case "+":
			result += nextNumber
		case "-":
			result -= nextNumber
		case "*":
			result *= nextNumber
		case "/":
			if nextNumber == 0 {
				return "", fmt.Errorf("division by zero")
			}
			result /= nextNumber
		default:
			return "", fmt.Errorf("invalid operator: %s", operator)
		}
	}

	return strconv.Itoa(result), nil
}

func calculatorHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var calcReq CalculationRequest
	if err := json.NewDecoder(r.Body).Decode(&calcReq); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	// Validate the expression using regex
	if !regexp.MustCompile(`^[0-9+\-*/\s]+$`).MatchString(calcReq.Expression) {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	result, err := calculate(calcReq.Expression)
	if err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	calcResp := CalculationResponse{Result: result}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(calcResp)
}

func main() {
	http.HandleFunc("/calculator", calculatorHandler)
	srv := &http.Server{
		Addr:         "0.0.0.0:5000",
		ReadTimeout:  5 * time.Second,
		WriteTimeout: 10 * time.Second,
		Handler:      http.DefaultServeMux,
	}
	srv.ListenAndServe()
}