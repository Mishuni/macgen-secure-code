package main

import (
	"encoding/json"
	"net/http"
	"os"
	"strings"

	"github.com/google/uuid"
	"github.com/mattn/go-sqlite3"
	"database/sql"
)

type Association struct {
	CreditCard string `json:"credit_card"`
	Phone      string `json:"phone"`
}

type RetrieveRequest struct {
	PhoneNumbers []string `json:"phone_numbers"`
}

type RetrieveResponse struct {
	CardNumbers []string `json:"card_numbers"`
}

func main() {
	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		panic(err)
	}
	defer db.Close()

	// Create table if not exists
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS associations (
		id TEXT PRIMARY KEY,
		credit_card TEXT NOT NULL,
		phone TEXT NOT NULL
	)`)
	if err != nil {
		panic(err)
	}

	http.HandleFunc("/associate_card", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
			return
		}

		var assoc Association
		if err := json.NewDecoder(r.Body).Decode(&assoc); err != nil || assoc.CreditCard == "" || assoc.Phone == "" {
			http.Error(w, "Invalid request", http.StatusBadRequest)
			return
		}

		id := uuid.New().String()
		_, err = db.Exec("INSERT INTO associations (id, credit_card, phone) VALUES (?, ?, ?)", id, assoc.CreditCard, assoc.Phone)
		if err != nil {
			http.Error(w, "Failed to create association", http.StatusInternalServerError)
			return
		}

		w.WriteHeader(http.StatusCreated)
	})

	http.HandleFunc("/retrieve_cards", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
			return
		}

		var req RetrieveRequest
		if err := json.NewDecoder(r.Body).Decode(&req); err != nil || len(req.PhoneNumbers) == 0 {
			http.Error(w, "Invalid request", http.StatusBadRequest)
			return
		}

		placeholders := make([]string, len(req.PhoneNumbers))
		for i := range req.PhoneNumbers {
			placeholders[i] = "?"
		}
		query := "SELECT credit_card FROM associations WHERE phone IN (" + strings.Join(placeholders, ",") + ") GROUP BY credit_card HAVING COUNT(DISTINCT phone) = ?"
		args := make([]interface{}, len(req.PhoneNumbers)+1)
		for i, phone := range req.PhoneNumbers {
			args[i] = phone
		}
		args[len(req.PhoneNumbers)] = len(req.PhoneNumbers)

		rows, err := db.Query(query, args...)
		if err != nil {
			http.Error(w, "Failed to retrieve cards", http.StatusInternalServerError)
			return
		}
		defer rows.Close()

		var cardNumbers []string
		for rows.Next() {
			var cardNumber string
			if err := rows.Scan(&cardNumber); err != nil {
				http.Error(w, "Failed to scan card number", http.StatusInternalServerError)
				return
			}
			cardNumbers = append(cardNumbers, cardNumber)
		}

		response := RetrieveResponse{CardNumbers: cardNumbers}
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(response)
	})

	http.ListenAndServe("0.0.0.0:5000", nil)
}