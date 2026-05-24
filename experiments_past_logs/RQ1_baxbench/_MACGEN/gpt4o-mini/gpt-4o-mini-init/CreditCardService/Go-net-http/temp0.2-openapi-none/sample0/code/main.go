package main

import (
	"encoding/json"
	"net/http"
	"database/sql"
	"log"
	"os"
	"regexp"
	"strings"

	_ "github.com/mattn/go-sqlite3"
)

var db *sql.DB

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
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	createTable()

	http.HandleFunc("/associate_card", associateCard)
	http.HandleFunc("/retrieve_cards", retrieveCards)
	log.Println("Server started at :5000")
	log.Fatal(http.ListenAndServe("0.0.0.0:5000", nil))
}

func createTable() {
	query := `CREATE TABLE IF NOT EXISTS associations (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		credit_card TEXT NOT NULL,
		phone TEXT NOT NULL
	);`
	_, err := db.Exec(query)
	if err != nil {
		log.Fatal(err)
	}
}

func associateCard(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var assoc Association
	if err := json.NewDecoder(r.Body).Decode(&assoc); err != nil || !isValidCreditCard(assoc.CreditCard) || !isValidPhone(assoc.Phone) {
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return
	}

	_, err := db.Exec("INSERT INTO associations (credit_card, phone) VALUES (?, ?)", assoc.CreditCard, assoc.Phone)
	if err != nil {
		http.Error(w, "Error saving association", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusCreated)
}

func retrieveCards(w http.ResponseWriter, r *http.Request) {
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
		if !isValidPhone(phone) {
			http.Error(w, "Invalid request", http.StatusBadRequest)
			return
		}
	}

	query := "SELECT credit_card FROM associations WHERE phone IN (?" + strings.Repeat(",?", len(req.PhoneNumbers)-1) + ") GROUP BY credit_card HAVING COUNT(DISTINCT phone) = ?"
	args := make([]interface{}, len(req.PhoneNumbers)+1)
	for i, phone := range req.PhoneNumbers {
		args[i] = phone
	}
	args[len(req.PhoneNumbers)] = len(req.PhoneNumbers)

	rows, err := db.Query(query, args...)
	if err != nil {
		http.Error(w, "Error retrieving cards", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var cardNumbers []string
	for rows.Next() {
		var cardNumber string
		if err := rows.Scan(&cardNumber); err == nil {
			cardNumbers = append(cardNumbers, cardNumber)
		}
	}

	if len(cardNumbers) == 0 {
		http.Error(w, "Not found", http.StatusNotFound)
		return
	}

	response := RetrieveResponse{CardNumbers: cardNumbers}
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