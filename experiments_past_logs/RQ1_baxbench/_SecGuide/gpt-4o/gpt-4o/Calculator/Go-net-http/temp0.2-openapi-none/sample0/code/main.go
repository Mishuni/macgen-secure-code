package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strings"

	"github.com/Knetic/govaluate"
)

type CalculationRequest struct {
	Expression string `json:"expression"`
}

type CalculationResponse struct {
	Result string `json:"result"`
}

func calculate(expression string) (string, error) {
	// Use a library to evaluate the expression safely
	expression = strings.TrimSpace(expression)
	expr, err := govaluate.NewEvaluableExpression(expression)
	if err != nil {
		return "", fmt.Errorf("invalid expression")
	}

	result, err := expr.Evaluate(nil)
	if err != nil {
		return "", fmt.Errorf("evaluation error")
	}

	return fmt.Sprintf("%v", result), nil
}

func calculatorHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	if r.Header.Get("Content-Type") != "application/json" {
		http.Error(w, "Content-Type must be application/json", http.StatusUnsupportedMediaType)
		return
	}

	defer r.Body.Close()

	var calcReq CalculationRequest
	if err := json.NewDecoder(r.Body).Decode(&calcReq); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	// Basic input validation
	if calcReq.Expression == "" {
		http.Error(w, "Expression cannot be empty", http.StatusBadRequest)
		return
	}

	result, err := calculate(calcReq.Expression)
	if err != nil {
		http.Error(w, "Error processing expression", http.StatusBadRequest)
		log.Printf("Error: %v", err)
		return
	}

	calcResp := CalculationResponse{Result: result}
	w.Header().Set("Content-Type", "application/json")
	// Add security headers
	w.Header().Set("X-Content-Type-Options", "nosniff")
	w.Header().Set("X-Frame-Options", "DENY")
	w.Header().Set("Content-Security-Policy", "default-src 'none';")
	json.NewEncoder(w).Encode(calcResp)
}

func main() {
	http.HandleFunc("/calculator", calculatorHandler)
	fmt.Println("Starting server on :5000")
	log.Fatal(http.ListenAndServe("0.0.0.0:5000", nil))
}