package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"regexp"

	_ "github.com/mattn/go-sqlite3"
)

var db *sql.DB

type AssociateCardRequest struct {
	CreditCard string `json:"credit_card"`
	Phone      string `json:"phone"`
}

type RetrieveCardsRequest struct {
	PhoneNumbers []string `json:"phone_numbers"`
}

type CardResponse struct {
	CardNumbers []string `json:"card_numbers"`
}

func main() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Create table if not exists
	createTableSQL := `CREATE TABLE IF NOT EXISTS card_associations (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		credit_card TEXT NOT NULL,
		phone TEXT NOT NULL
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		log.Fatal(err)
	}

	http.HandleFunc("/associate_card", associateCardHandler)
	http.HandleFunc("/retrieve_cards", retrieveCardsHandler)

	log.Println("Server started at :5000")
	if err := http.ListenAndServe(":5000", nil); err != nil {
		log.Fatal(err)
	}
}

func associateCardHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var req AssociateCardRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	if !isValidCreditCard(req.CreditCard) || !isValidPhone(req.Phone) {
		http.Error(w, "Invalid credit card or phone number", http.StatusBadRequest)
		return
	}

	_, err := db.Exec("INSERT INTO card_associations (credit_card, phone) VALUES (?, ?)", req.CreditCard, req.Phone)
	if err != nil {
		http.Error(w, "Failed to associate card", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusCreated)
}

func retrieveCardsHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var req RetrieveCardsRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	if len(req.PhoneNumbers) == 0 {
		http.Error(w, "Phone numbers are required", http.StatusBadRequest)
		return
	}

	query := "SELECT credit_card FROM card_associations WHERE phone IN (?" + strings.Repeat(",?", len(req.PhoneNumbers)-1) + ") GROUP BY credit_card HAVING COUNT(DISTINCT phone) = ?"
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

	response := CardResponse{CardNumbers: cardNumbers}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func isValidCreditCard(card string) bool {
	re := regexp.MustCompile(`^\d{16}$`)
	return re.MatchString(card)
}

func isValidPhone(phone string) bool {
	re := regexp.MustCompile(`^\d{1}-\d{3}-\d{3}$`)
	return re.MatchString(phone)
}