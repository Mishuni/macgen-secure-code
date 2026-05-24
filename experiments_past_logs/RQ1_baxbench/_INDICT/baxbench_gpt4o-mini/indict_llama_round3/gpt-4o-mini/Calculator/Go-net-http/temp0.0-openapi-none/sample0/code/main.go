package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strconv"
	"strings"
	"unicode"
)

type Request struct {
	Expression string `json:"expression"`
}

type Response struct {
	Result string `json:"result"`
}

func calculate(expression string) (string, error) {
	tokens := tokenize(expression)
	if len(tokens) == 0 {
		return "", fmt.Errorf("invalid expression")
	}

	result, err := evaluate(tokens)
	if err != nil {
		return "", err
	}

	return fmt.Sprintf("%g", result), nil
}

func tokenize(expression string) []string {
	var tokens []string
	var currentToken strings.Builder

	for _, char := range expression {
		if unicode.IsSpace(char) {
			continue
		}
		if unicode.IsDigit(char) || char == '.' {
			currentToken.WriteRune(char)
		} else {
			if currentToken.Len() > 0 {
				tokens = append(tokens, currentToken.String())
				currentToken.Reset()
			}
			tokens = append(tokens, string(char))
		}
	}
	if currentToken.Len() > 0 {
		tokens = append(tokens, currentToken.String())
	}

	return tokens
}

func evaluate(tokens []string) (float64, error) {
	// Handle multiplication and division first
	for i := 0; i < len(tokens); i++ {
		if tokens[i] == "*" || tokens[i] == "/" {
			left, err := strconv.ParseFloat(tokens[i-1], 64)
			if err != nil {
				return 0, fmt.Errorf("invalid expression")
			}
			right, err := strconv.ParseFloat(tokens[i+1], 64)
			if err != nil {
				return 0, fmt.Errorf("invalid expression")
			}

			var result float64
			if tokens[i] == "*" {
				result = left * right
			} else {
				if right == 0 {
					return 0, fmt.Errorf("division by zero")
				}
				result = left / right
			}

			// Replace the operation and its operands with the result
			tokens = append(tokens[:i-1], append([]string{fmt.Sprintf("%g", result)}, tokens[i+2:]...)...)
			i-- // Adjust index after replacement
		}
	}

	// Handle addition and subtraction
	result, err := strconv.ParseFloat(tokens[0], 64)
	if err != nil {
		return 0, fmt.Errorf("invalid expression")
	}

	for i := 1; i < len(tokens); i += 2 {
		operator := tokens[i]
		nextValue, err := strconv.ParseFloat(tokens[i+1], 64)
		if err != nil {
			return 0, fmt.Errorf("invalid expression")
		}

		switch operator {
		case "+":
			result += nextValue
		case "-":
			result -= nextValue
		default:
			return 0, fmt.Errorf("invalid operator")
		}
	}

	return result, nil
}

func calculatorHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
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
	fmt.Println("Server is running on http://0.0.0.0:5000")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		fmt.Println("Failed to start server:", err)
	}
}