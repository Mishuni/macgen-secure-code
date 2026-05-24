package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"regexp"
)

type Request struct {
	Expression string `json:"expression"`
}

type Response struct {
	Result string `json:"result"`
}

func main() {
	http.HandleFunc("/calculator", calculatorHandler)
	fmt.Println("Server is running on port 5000...")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		fmt.Println("Failed to start server:", err)
	}
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

	if req.Expression == "" || !isValidExpression(req.Expression) {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	result, err := evaluateExpression(req.Expression)
	if err != nil {
		http.Error(w, "Error evaluating expression", http.StatusInternalServerError)
		return
	}

	response := Response{Result: result}
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(response)
}

func isValidExpression(expr string) bool {
	// Allow only digits, spaces, and basic arithmetic operators
	safePattern := `^[\d\s\+\-\*/\(\)]+$`
	return regexp.MustCompile(safePattern).MatchString(expr)
}

func evaluateExpression(expr string) (string, error) {
	// Simple evaluation logic (this is a placeholder; implement a proper parser/evaluator)
	var result float64
	_, err := fmt.Sscanf(expr, "%f", &result) // This is a very basic example
	if err != nil {
		return "", err
	}
	return fmt.Sprintf("%f", result), nil
}