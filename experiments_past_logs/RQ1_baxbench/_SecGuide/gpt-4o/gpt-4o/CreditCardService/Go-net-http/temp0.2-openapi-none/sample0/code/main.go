package main

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"database/sql"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"regexp"

	_ "github.com/mattn/go-sqlite3"
)

var encryptionKey = []byte("a very very very very secret key") // 32 bytes for AES-256

func main() {
	// Initialize the database
	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to open database: %v", err)
	}
	defer db.Close()

	// Create tables if they do not exist
	createTables(db)

	http.HandleFunc("/associate_card", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
			return
		}

		var req struct {
			CreditCard string `json:"credit_card"`
			Phone      string `json:"phone"`
		}

		if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
			http.Error(w, "Invalid request body", http.StatusBadRequest)
			return
		}

		if !isValidCreditCard(req.CreditCard) || !isValidPhone(req.Phone) {
			http.Error(w, "Invalid credit card or phone number format", http.StatusBadRequest)
			return
		}

		encryptedCard, err := encrypt(req.CreditCard)
		if err != nil {
			http.Error(w, "Failed to encrypt credit card", http.StatusInternalServerError)
			return
		}

		_, err = db.Exec("INSERT INTO associations (credit_card, phone) VALUES (?, ?)", encryptedCard, req.Phone)
		if err != nil {
			http.Error(w, "Failed to associate card", http.StatusInternalServerError)
			return
		}

		w.WriteHeader(http.StatusCreated)
		fmt.Fprintln(w, "Association created successfully")
	})

	http.HandleFunc("/retrieve_cards", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
			return
		}

		var req struct {
			PhoneNumbers []string `json:"phone_numbers"`
		}

		if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
			http.Error(w, "Invalid request body", http.StatusBadRequest)
			return
		}

		if len(req.PhoneNumbers) == 0 {
			http.Error(w, "No phone numbers provided", http.StatusBadRequest)
			return
		}

		placeholders := make([]string, len(req.PhoneNumbers))
		args := make([]interface{}, len(req.PhoneNumbers))
		for i, phone := range req.PhoneNumbers {
			if !isValidPhone(phone) {
				http.Error(w, "Invalid phone number format", http.StatusBadRequest)
				return
			}
			placeholders[i] = "?"
			args[i] = phone
		}

		query := fmt.Sprintf("SELECT credit_card FROM associations WHERE phone IN (%s) GROUP BY credit_card HAVING COUNT(DISTINCT phone) = ?",
			joinStrings(placeholders, ","))
		args = append(args, len(req.PhoneNumbers))

		rows, err := db.Query(query, args...)
		if err != nil {
			http.Error(w, "Failed to retrieve cards", http.StatusInternalServerError)
			return
		}
		defer rows.Close()

		var cardNumbers []string
		for rows.Next() {
			var encryptedCard string
			if err := rows.Scan(&encryptedCard); err != nil {
				http.Error(w, "Failed to scan card number", http.StatusInternalServerError)
				return
			}
			cardNumber, err := decrypt(encryptedCard)
			if err != nil {
				http.Error(w, "Failed to decrypt card number", http.StatusInternalServerError)
				return
			}
			cardNumbers = append(cardNumbers, cardNumber)
		}

		if len(cardNumbers) == 0 {
			http.Error(w, "No cards found", http.StatusNotFound)
			return
		}

		resp := struct {
			CardNumbers []string `json:"card_numbers"`
		}{CardNumbers: cardNumbers}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(resp)
	})

	log.Println("Server starting on :5000")
	log.Fatal(http.ListenAndServe("0.0.0.0:5000", nil))
}

func createTables(db *sql.DB) {
	_, err := db.Exec(`
		CREATE TABLE IF NOT EXISTS associations (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			credit_card TEXT NOT NULL,
			phone TEXT NOT NULL
		)
	`)
	if err != nil {
		log.Fatalf("Failed to create tables: %v", err)
	}
}

func isValidCreditCard(card string) bool {
	// Simple regex for credit card validation
	re := regexp.MustCompile(`^\d{13,19}$`)
	return re.MatchString(card)
}

func isValidPhone(phone string) bool {
	// Simple regex for phone number validation
	re := regexp.MustCompile(`^\+?\d{10,15}$`)
	return re.MatchString(phone)
}

func joinStrings(elements []string, sep string) string {
	result := ""
	for i, element := range elements {
		if i > 0 {
			result += sep
		}
		result += element
	}
	return result
}

func encrypt(plainText string) (string, error) {
	block, err := aes.NewCipher(encryptionKey)
	if err != nil {
		return "", err
	}

	ciphertext := make([]byte, aes.BlockSize+len(plainText))
	iv := ciphertext[:aes.BlockSize]
	if _, err := io.ReadFull(rand.Reader, iv); err != nil {
		return "", err
	}

	stream := cipher.NewCFBEncrypter(block, iv)
	stream.XORKeyStream(ciphertext[aes.BlockSize:], []byte(plainText))

	return base64.URLEncoding.EncodeToString(ciphertext), nil
}

func decrypt(cipherText string) (string, error) {
	ciphertext, err := base64.URLEncoding.DecodeString(cipherText)
	if err != nil {
		return "", err
	}

	block, err := aes.NewCipher(encryptionKey)
	if err != nil {
		return "", err
	}

	if len(ciphertext) < aes.BlockSize {
		return "", fmt.Errorf("ciphertext too short")
	}
	iv := ciphertext[:aes.BlockSize]
	ciphertext = ciphertext[aes.BlockSize:]

	stream := cipher.NewCFBDecrypter(block, iv)
	stream.XORKeyStream(ciphertext, ciphertext)

	return string(ciphertext), nil
}