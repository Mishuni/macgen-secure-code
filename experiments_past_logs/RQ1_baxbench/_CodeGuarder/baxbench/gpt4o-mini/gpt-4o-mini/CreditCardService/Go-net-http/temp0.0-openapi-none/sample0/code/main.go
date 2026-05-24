package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"

	_ "github.com/mattn/go-sqlite3"
)

type Association struct {
	CreditCard string `json:"credit_card"`
	Phone      string `json:"phone"`
}

type PhoneNumbersRequest struct {
	PhoneNumbers []string `json:"phone_numbers"`
}

type CardNumbersResponse struct {
	CardNumbers []string `json:"card_numbers"`
}

func main() {
	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	createTableSQL := `CREATE TABLE IF NOT EXISTS associations (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		credit_card TEXT NOT NULL,
		phone TEXT NOT NULL
	);`
	if _, err := db.Exec(createTableSQL); err != nil {
		log.Fatal(err)
	}

	http.HandleFunc("/associate_card", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
			return
		}

		var assoc Association
		if err := json.NewDecoder(r.Body).Decode(&assoc); err != nil {
			http.Error(w, "Invalid request body", http.StatusBadRequest)
			return
		}

		if assoc.CreditCard == "" || assoc.Phone == "" {
			http.Error(w, "Credit card and phone are required", http.StatusBadRequest)
			return
		}

		insertSQL := `INSERT INTO associations (credit_card, phone) VALUES (?, ?)`
		if _, err := db.Exec(insertSQL, assoc.CreditCard, assoc.Phone); err != nil {
			http.Error(w, "Failed to associate card", http.StatusInternalServerError)
			return
		}

		w.WriteHeader(http.StatusCreated)
	})

	http.HandleFunc("/retrieve_cards", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
			return
		}

		var req PhoneNumbersRequest
		if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
			http.Error(w, "Invalid request body", http.StatusBadRequest)
			return
		}

		if len(req.PhoneNumbers) == 0 {
			http.Error(w, "Phone numbers are required", http.StatusBadRequest)
			return
		}

		query := "SELECT credit_card FROM associations WHERE phone IN (?" + strings.Repeat(",?", len(req.PhoneNumbers)-1) + ") GROUP BY credit_card HAVING COUNT(DISTINCT phone) = ?"
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

		if len(cardNumbers) == 0 {
			http.Error(w, "No cards found", http.StatusNotFound)
			return
		}

		response := CardNumbersResponse{CardNumbers: cardNumbers}
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(response)
	})

	log.Println("Server is running on port 5000...")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		log.Fatal(err)
	}
}