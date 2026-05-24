package main

import (
	"database/sql"
	"encoding/json"
	"log"
	"net/http"
	"os"

	"github.com/mattn/go-sqlite3"
)

var db *sql.DB

func init() {
	var err error
	// Initialize SQLite3 database
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}

	// Create tables if they do not exist
	createTableQuery := `
	CREATE TABLE IF NOT EXISTS card_phone_associations (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		credit_card TEXT NOT NULL,
		phone TEXT NOT NULL
	);
	`
	_, err = db.Exec(createTableQuery)
	if err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}
}

func main() {
	defer db.Close()

	http.HandleFunc("/associate_card", associateCardHandler)
	http.HandleFunc("/retrieve_cards", retrieveCardsHandler)

	log.Println("Server is running on 0.0.0.0:5000")
	log.Fatal(http.ListenAndServe("0.0.0.0:5000", nil))
}

func associateCardHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var reqBody struct {
		CreditCard string `json:"credit_card"`
		Phone      string `json:"phone"`
	}

	decoder := json.NewDecoder(r.Body)
	if err := decoder.Decode(&reqBody); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	if reqBody.CreditCard == "" || reqBody.Phone == "" {
		http.Error(w, "Missing required fields", http.StatusBadRequest)
		return
	}

	// Insert the association into the database using parameterized query
	query := "INSERT INTO card_phone_associations (credit_card, phone) VALUES (?, ?)"
	_, err := db.Exec(query, reqBody.CreditCard, reqBody.Phone)
	if err != nil {
		http.Error(w, "Failed to create association", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusCreated)
	w.Write([]byte("Association created successfully"))
}

func retrieveCardsHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var reqBody struct {
		PhoneNumbers []string `json:"phone_numbers"`
	}

	decoder := json.NewDecoder(r.Body)
	if err := decoder.Decode(&reqBody); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	if len(reqBody.PhoneNumbers) == 0 {
		http.Error(w, "Missing required fields", http.StatusBadRequest)
		return
	}

	// Build the query dynamically based on the number of phone numbers
	query := "SELECT DISTINCT credit_card FROM card_phone_associations WHERE phone IN (?" + strings.Repeat(", ?", len(reqBody.PhoneNumbers)-1) + ") GROUP BY credit_card HAVING COUNT(DISTINCT phone) = ?"
	args := make([]interface{}, len(reqBody.PhoneNumbers)+1)
	for i, phone := range reqBody.PhoneNumbers {
		args[i] = phone
	}
	args[len(reqBody.PhoneNumbers)] = len(reqBody.PhoneNumbers)

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
			http.Error(w, "Failed to parse database result", http.StatusInternalServerError)
			return
		}
		cardNumbers = append(cardNumbers, cardNumber)
	}

	if len(cardNumbers) == 0 {
		http.Error(w, "Not found", http.StatusNotFound)
		return
	}

	response := struct {
		CardNumbers []string `json:"card_numbers"`
	}{
		CardNumbers: cardNumbers,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}