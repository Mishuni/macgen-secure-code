package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strconv"
	"strings"
	"log"
	"regexp"
)

type Request struct {
	Expression string `json:"expression"`
}

type Response struct {
	Result string `json:"result"`
}

func calculate(expression string) (string, error) {
	// Validate the expression format
	if !isValidExpression(expression) {
		return "", fmt.Errorf("invalid expression format")
	}

	tokens := strings.Fields(expression)
	if len(tokens) != 3 {
		return "", fmt.Errorf("invalid expression")
	}

	num1, err := strconv.Atoi(tokens[0])
	if err != nil {
		return "", err
	}
	operator := tokens[1]
	num2, err := strconv.Atoi(tokens[2])
	if err != nil {
		return "", err
	}

	var result int
	switch operator {
	case "+":
		result = num1 + num2
	case "-":
		result = num1 - num2
	case "*":
		result = num1 * num2
	case "/":
		if num2 == 0 {
			return "", fmt.Errorf("division by zero")
		}
		result = num1 / num2
	default:
		return "", fmt.Errorf("unsupported operator")
	}

	return strconv.Itoa(result), nil
}

func isValidExpression(expression string) bool {
	// Regular expression to match the expected format: number operator number
	re := regexp.MustCompile(`^\s*-?\d+\s*[\+\-\*/]\s*-?\d+\s*$`)
	return re.MatchString(expression)
}

func calculatorHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		w.Header().Set("Allow", http.MethodPost)
		return
	}

	if r.Header.Get("Content-Type") != "application/json" {
		http.Error(w, "Content-Type must be application/json", http.StatusUnsupportedMediaType)
		return
	}

	var req Request
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		log.Println("Error decoding request:", err)
		return
	}

	result, err := calculate(req.Expression)
	if err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		log.Println("Calculation error:", err)
		return
	}

	resp := Response{Result: result}
	w.Header().Set("Content-Type", "application/json")
	if err := json.NewEncoder(w).Encode(resp); err != nil {
		http.Error(w, "Error encoding response", http.StatusInternalServerError)
		log.Println("Error encoding response:", err)
		return
	}
}

func main() {
	http.HandleFunc("/calculator", calculatorHandler)
	fmt.Println("Server is running on http://0.0.0.0:5000")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		log.Fatal("Failed to start server:", err)
	}
}