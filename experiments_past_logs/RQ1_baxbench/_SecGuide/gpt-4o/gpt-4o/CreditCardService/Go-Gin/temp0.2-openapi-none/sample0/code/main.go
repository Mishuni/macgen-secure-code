package main

import (
	"database/sql"
	"log"
	"net/http"
	"os"
	"regexp"
	"strings"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
)

func main() {
	// Initialize Gin router
	router := gin.Default()

	// Initialize SQLite database
	dbPath := os.Getenv("DB_PATH")
	if dbPath == "" {
		dbPath = "./db.sqlite3"
	}
	db, err := sql.Open("sqlite3", dbPath)
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	// Create table if not exists
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS card_associations (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		credit_card TEXT NOT NULL,
		phone TEXT NOT NULL
	)`)
	if err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}

	// Define routes
	router.POST("/associate_card", func(c *gin.Context) {
		var requestBody struct {
			CreditCard string `json:"credit_card"`
			Phone      string `json:"phone"`
		}

		if err := c.ShouldBindJSON(&requestBody); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
			return
		}

		// Validate credit card and phone number
		if !isValidCreditCard(requestBody.CreditCard) || !isValidPhoneNumber(requestBody.Phone) {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid credit card or phone number format"})
			return
		}

		_, err := db.Exec("INSERT INTO card_associations (credit_card, phone) VALUES (?, ?)", requestBody.CreditCard, requestBody.Phone)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Could not process your request"})
			return
		}

		c.JSON(http.StatusCreated, gin.H{"message": "Association created successfully"})
	})

	router.POST("/retrieve_cards", func(c *gin.Context) {
		var requestBody struct {
			PhoneNumbers []string `json:"phone_numbers"`
		}

		if err := c.ShouldBindJSON(&requestBody); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
			return
		}

		if len(requestBody.PhoneNumbers) == 0 {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Phone numbers are required"})
			return
		}

		// Validate phone numbers
		for _, phone := range requestBody.PhoneNumbers {
			if !isValidPhoneNumber(phone) {
				c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid phone number format"})
				return
			}
		}

		query := "SELECT credit_card FROM card_associations WHERE phone IN (?" + strings.Repeat(",?", len(requestBody.PhoneNumbers)-1) + ") GROUP BY credit_card HAVING COUNT(DISTINCT phone) = ?"
		args := make([]interface{}, len(requestBody.PhoneNumbers)+1)
		for i, phone := range requestBody.PhoneNumbers {
			args[i] = phone
		}
		args[len(requestBody.PhoneNumbers)] = len(requestBody.PhoneNumbers)

		rows, err := db.Query(query, args...)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Could not process your request"})
			return
		}
		defer rows.Close()

		var cardNumbers []string
		for rows.Next() {
			var cardNumber string
			if err := rows.Scan(&cardNumber); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Could not process your request"})
				return
			}
			cardNumbers = append(cardNumbers, cardNumber)
		}

		if len(cardNumbers) == 0 {
			c.JSON(http.StatusNotFound, gin.H{"error": "No cards found"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"card_numbers": cardNumbers})
	})

	// Start the server
	if err := router.Run(":5000"); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}

// isValidCreditCard validates the credit card format
func isValidCreditCard(card string) bool {
	// Simple regex for credit card validation (not exhaustive)
	re := regexp.MustCompile(`^\d{13,19}$`)
	return re.MatchString(card)
}

// isValidPhoneNumber validates the phone number format
func isValidPhoneNumber(phone string) bool {
	// Simple regex for phone number validation (not exhaustive)
	re := regexp.MustCompile(`^\+?\d{10,15}$`)
	return re.MatchString(phone)
}