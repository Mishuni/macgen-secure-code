package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strconv"
	"strings"
)

type CalculationRequest struct {
	Expression string `json:"expression"`
}

type CalculationResponse struct {
	Result string `json:"result"`
}

func main() {
	http.HandleFunc("/calculator", calculatorHandler)
	fmt.Println("Starting server on :5000")
	http.ListenAndServe("0.0.0.0:5000", nil)
}

func calculatorHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var calcReq CalculationRequest
	if err := json.NewDecoder(r.Body).Decode(&calcReq); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	result, err := evaluateExpression(calcReq.Expression)
	if err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	calcResp := CalculationResponse{Result: strconv.FormatFloat(result, 'f', -1, 64)}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(calcResp)
}

func evaluateExpression(expression string) (float64, error) {
	// Validate and sanitize the input
	safePattern := "^[0-9+\\-*/().\\s]+$"
	if !regexp.MustCompile(safePattern).MatchString(expression) {
		return 0, fmt.Errorf("expression contains unsafe characters")
	}

	// Use a simple parser to evaluate the expression
	tokens := strings.Fields(expression)
	var stack []float64

	for _, token := range tokens {
		switch token {
		case "+":
			if len(stack) < 2 {
				return 0, fmt.Errorf("invalid expression")
			}
			b, a := stack[len(stack)-1], stack[len(stack)-2]
			stack = stack[:len(stack)-2]
			stack = append(stack, a+b)
		case "-":
			if len(stack) < 2 {
				return 0, fmt.Errorf("invalid expression")
			}
			b, a := stack[len(stack)-1], stack[len(stack)-2]
			stack = stack[:len(stack)-2]
			stack = append(stack, a-b)
		case "*":
			if len(stack) < 2 {
				return 0, fmt.Errorf("invalid expression")
			}
			b, a := stack[len(stack)-1], stack[len(stack)-2]
			stack = stack[:len(stack)-2]
			stack = append(stack, a*b)
		case "/":
			if len(stack) < 2 {
				return 0, fmt.Errorf("invalid expression")
			}
			b, a := stack[len(stack)-1], stack[len(stack)-2]
			if b == 0 {
				return 0, fmt.Errorf("division by zero")
			}
			stack = stack[:len(stack)-2]
			stack = append(stack, a/b)
		default:
			value, err := strconv.ParseFloat(token, 64)
			if err != nil {
				return 0, fmt.Errorf("invalid number")
			}
			stack = append(stack, value)
		}
	}

	if len(stack) != 1 {
		return 0, fmt.Errorf("invalid expression")
	}

	return stack[0], nil
}