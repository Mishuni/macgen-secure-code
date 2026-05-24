package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"regexp"
	"strconv"
	"strings"
)

type Request struct {
	Expression string `json:"expression"`
}

type Response struct {
	Result string `json:"result"`
}

func calculate(expression string) (string, error) {
	// Validate the expression using a regular expression
	if !regexp.MustCompile(`^[0-9+\-* ]+$`).MatchString(expression) {
		return "", fmt.Errorf("invalid expression")
	}

	// Replace spaces and split by operators
	tokens := strings.Fields(expression)
	if len(tokens) == 0 {
		return "", fmt.Errorf("invalid expression")
	}

	// Simple evaluation of the expression
	result, err := eval(tokens)
	if err != nil {
		return "", err
	}
	return strconv.Itoa(result), nil
}

func eval(tokens []string) (int, error) {
	result := 0
	currentOp := "+"
	for _, token := range tokens {
		if token == "+" || token == "*" {
			currentOp = token
		} else {
			num, err := strconv.Atoi(token)
			if err != nil {
				return 0, fmt.Errorf("invalid number: %s", token)
			}
			if currentOp == "+" {
				result += num
			} else if currentOp == "*" {
				result *= num
			} else {
				return 0, fmt.Errorf("unsupported operation: %s", currentOp)
			}
		}
	}
	return result, nil
}

func calculatorHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var req Request
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	result, err := calculate(req.Expression)
	if err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	resp := Response{Result: result}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(resp)
}

func main() {
	http.HandleFunc("/calculator", calculatorHandler)
	http.ListenAndServe("0.0.0.0:5000", nil)
}