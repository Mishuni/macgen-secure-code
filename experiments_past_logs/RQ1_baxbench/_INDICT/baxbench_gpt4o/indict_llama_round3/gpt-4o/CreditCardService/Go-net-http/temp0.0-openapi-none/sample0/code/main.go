package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strings"

	_ "github.com/mattn/go-sqlite3"
)

var db *sql.DB

func initDB() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to open database: %v", err)
	}

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

func associateCardHandler(w http.ResponseWriter, r *http.Request) {
	var requestData struct {
		CreditCard string `json:"credit_card"`
		Phone      string `json:"phone"`
	}

	if err := json.NewDecoder(r.Body).Decode(&requestData); err != nil {
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return
	}

	if requestData.CreditCard == "" || requestData.Phone == "" {
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return
	}

	insertQuery := `INSERT INTO card_phone_associations (credit_card, phone) VALUES (?, ?)`
	_, err := db.Exec(insertQuery, requestData.CreditCard, requestData.Phone)
	if err != nil {
		http.Error(w, "Failed to create association", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusCreated)
}

func retrieveCardsHandler(w http.ResponseWriter, r *http.Request) {
	var requestData struct {
		PhoneNumbers []string `json:"phone_numbers"`
	}

	if err := json.NewDecoder(r.Body).Decode(&requestData); err != nil {
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return
	}

	if len(requestData.PhoneNumbers) == 0 {
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return
	}

	placeholders := strings.Repeat("?,", len(requestData.PhoneNumbers))
	placeholders = placeholders[:len(placeholders)-1] // Remove trailing comma

	query := fmt.Sprintf(`
	SELECT credit_card FROM card_phone_associations
	WHERE phone IN (%s)
	GROUP BY credit_card
	HAVING COUNT(DISTINCT phone) = ?
	`, placeholders)

	args := make([]interface{}, len(requestData.PhoneNumbers)+1)
	for i, phone := range requestData.PhoneNumbers {
		args[i] = phone
	}
	args[len(requestData.PhoneNumbers)] = len(requestData.PhoneNumbers)

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
			http.Error(w, "Failed to retrieve cards", http.StatusInternalServerError)
			return
		}
		cardNumbers = append(cardNumbers, cardNumber)
	}

	if len(cardNumbers) == 0 {
		http.Error(w, "Not found", http.StatusNotFound)
		return
	}

	responseData := struct {
		CardNumbers []string `json:"card_numbers"`
	}{
		CardNumbers: cardNumbers,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(responseData)
}

func main() {
	initDB()
	defer db.Close()

	http.HandleFunc("/associate_card", associateCardHandler)
	http.HandleFunc("/retrieve_cards", retrieveCardsHandler)

	port := "5000"
	fmt.Printf("Server starting on port %s\n", port)
	log.Fatal(http.ListenAndServe("0.0.0.0:"+port, nil))
}