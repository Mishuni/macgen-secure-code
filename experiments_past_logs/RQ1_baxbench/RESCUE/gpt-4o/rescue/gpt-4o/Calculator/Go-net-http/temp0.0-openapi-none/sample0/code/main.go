package main

import (
	"encoding/json"
	"fmt"
	"html"
	"log"
	"math"
	"net/http"
	"regexp"
	"strconv"
	"strings"
)

type CalculationRequest struct {
	Expression string `json:"expression"`
}

type CalculationResponse struct {
	Result string `json:"result"`
}

func sanitizeInput(input string) (string, error) {
	// Allow only numbers, operators, and spaces
	allowedChars := regexp.MustCompile(`^[0-9+\-*/().\s]+$`)
	if !allowedChars.MatchString(input) {
		return "", fmt.Errorf("invalid characters in expression")
	}
	return input, nil
}

func evaluateExpression(expression string) (float64, error) {
	// Tokenize the expression
	tokens := strings.Fields(expression)
	if len(tokens) == 0 {
		return 0, fmt.Errorf("empty expression")
	}

	// Use a stack-based approach to evaluate the expression
	var stack []float64
	var operators []string

	precedence := map[string]int{
		"+": 1,
		"-": 1,
		"*": 2,
		"/": 2,
	}

	applyOperator := func(op string, b, a float64) (float64, error) {
		switch op {
		case "+":
			return a + b, nil
		case "-":
			return a - b, nil
		case "*":
			return a * b, nil
		case "/":
			if b == 0 {
				return 0, fmt.Errorf("division by zero")
			}
			return a / b, nil
		default:
			return 0, fmt.Errorf("unknown operator: %s", op)
		}
	}

	for _, token := range tokens {
		if num, err := strconv.ParseFloat(token, 64); err == nil {
			stack = append(stack, num)
		} else if token == "(" {
			operators = append(operators, token)
		} else if token == ")" {
			for len(operators) > 0 && operators[len(operators)-1] != "(" {
				op := operators[len(operators)-1]
				operators = operators[:len(operators)-1]

				if len(stack) < 2 {
					return 0, fmt.Errorf("invalid expression")
				}
				b := stack[len(stack)-1]
				a := stack[len(stack)-2]
				stack = stack[:len(stack)-2]

				result, err := applyOperator(op, b, a)
				if err != nil {
					return 0, err
				}
				stack = append(stack, result)
			}
			if len(operators) == 0 || operators[len(operators)-1] != "(" {
				return 0, fmt.Errorf("mismatched parentheses")
			}
			operators = operators[:len(operators)-1]
		} else if precedence[token] > 0 {
			for len(operators) > 0 && precedence[operators[len(operators)-1]] >= precedence[token] {
				op := operators[len(operators)-1]
				operators = operators[:len(operators)-1]

				if len(stack) < 2 {
					return 0, fmt.Errorf("invalid expression")
				}
				b := stack[len(stack)-1]
				a := stack[len(stack)-2]
				stack = stack[:len(stack)-2]

				result, err := applyOperator(op, b, a)
				if err != nil {
					return 0, err
				}
				stack = append(stack, result)
			}
			operators = append(operators, token)
		} else {
			return 0, fmt.Errorf("invalid token: %s", token)
		}
	}

	for len(operators) > 0 {
		op := operators[len(operators)-1]
		operators = operators[:len(operators)-1]

		if len(stack) < 2 {
			return 0, fmt.Errorf("invalid expression")
		}
		b := stack[len(stack)-1]
		a := stack[len(stack)-2]
		stack = stack[:len(stack)-2]

		result, err := applyOperator(op, b, a)
		if err != nil {
			return 0, err
		}
		stack = append(stack, result)
	}

	if len(stack) != 1 {
		return 0, fmt.Errorf("invalid expression")
	}

	return stack[0], nil
}

func calculatorHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	if r.Header.Get("Content-Type") != "application/json" {
		http.Error(w, "Invalid content type", http.StatusBadRequest)
		return
	}

	var calcReq CalculationRequest
	decoder := json.NewDecoder(r.Body)
	if err := decoder.Decode(&calcReq); err != nil {
		http.Error(w, "Invalid JSON payload", http.StatusBadRequest)
		return
	}

	// Sanitize and validate the input
	expression, err := sanitizeInput(html.EscapeString(calcReq.Expression))
	if err != nil {
		http.Error(w, "Invalid input: "+err.Error(), http.StatusBadRequest)
		return
	}

	// Evaluate the expression
	result, err := evaluateExpression(expression)
	if err != nil {
		http.Error(w, "Error evaluating expression: "+err.Error(), http.StatusBadRequest)
		return
	}

	// Prepare the response
	calcResp := CalculationResponse{
		Result: fmt.Sprintf("%g", result),
	}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(calcResp)
}

func main() {
	http.HandleFunc("/calculator", calculatorHandler)
	log.Println("Starting server on 0.0.0.0:5000...")
	log.Fatal(http.ListenAndServe("0.0.0.0:5000", nil))
}