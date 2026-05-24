package main

import (
	"encoding/json"
	"net/http"
	"os"
	"database/sql"
	"log"
	"regexp"
	"strings"

	_ "github.com/mattn/go-sqlite3"
)

type AssociationRequest struct {
	CreditCard string `json:"credit_card"`
	Phone      string `json:"phone"`
}

type RetrieveRequest struct {
	PhoneNumbers []string `json:"phone_numbers"`
}

type RetrieveResponse struct {
	CardNumbers []string `json:"card_numbers"`
}

func validateCreditCard(card string) bool {
	// Improved regex for credit card format validation
	re := regexp.MustCompile(`^(?:\d{4}[- ]?){3}\d{4}$`)
	return re.MatchString(card)
}

func validatePhoneNumber(phone string) bool {
	// Improved regex for phone number format validation
	re := regexp.MustCompile(`^\+?\d{10,15}$`)
	return re.MatchString(phone)
}

func main() {
	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Create table if not exists
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

		var req AssociationRequest
		if err := json.NewDecoder(r.Body).Decode(&req); err != nil || req.CreditCard == "" || req.Phone == "" {
			http.Error(w, "Invalid request", http.StatusBadRequest)
			return
		}

		if !validateCreditCard(req.CreditCard) || !validatePhoneNumber(req.Phone) {
			http.Error(w, "Invalid credit card or phone number format", http.StatusBadRequest)
			return
		}

		_, err := db.Exec("INSERT INTO associations (credit_card, phone) VALUES (?, ?)", req.CreditCard, req.Phone)
		if err != nil {
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

		var req RetrieveRequest
		if err := json.NewDecoder(r.Body).Decode(&req); err != nil || len(req.PhoneNumbers) == 0 {
			http.Error(w, "Invalid request", http.StatusBadRequest)
			return
		}

		for _, phone := range req.PhoneNumbers {
			if !validatePhoneNumber(phone) {
				http.Error(w, "Invalid phone number format", http.StatusBadRequest)
				return
			}
		}

		query := "SELECT credit_card FROM associations WHERE phone IN (?" + strings.Repeat(",?", len(req.PhoneNumbers)-1) + ")"
		args := make([]interface{}, len(req.PhoneNumbers))
		for i, phone := range req.PhoneNumbers {
			args[i] = phone
		}

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

	log.Println("Server starting on :5000")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		log.Fatal(err)
	}
}