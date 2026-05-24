package main

import (
	"database/sql"
	"log"
	"net/http"
	"strings"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
)

type Association struct {
	CreditCard string `json:"credit_card"`
	Phone      string `json:"phone"`
}

type RetrieveRequest struct {
	PhoneNumbers []string `json:"phone_numbers"`
}

func main() {
	// Initialize the database
	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Create the table if it doesn't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS associations (
		credit_card TEXT,
		phone TEXT
	)`)
	if err != nil {
		log.Fatal(err)
	}

	// Set up the Gin router
	r := gin.New()

	// Define the /associate_card endpoint
	r.POST("/associate_card", func(c *gin.Context) {
		var assoc Association
		if err := c.ShouldBindJSON(&assoc); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
			return
		}

		if !isValidCreditCard(assoc.CreditCard) || !isValidPhone(assoc.Phone) {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid credit card or phone number format"})
			return
		}

		_, err := db.Exec("INSERT INTO associations (credit_card, phone) VALUES (?, ?)", assoc.CreditCard, assoc.Phone)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Failed to create association"})
			return
		}

		c.JSON(http.StatusCreated, gin.H{"message": "Association created successfully"})
	})

	// Define the /retrieve_cards endpoint
	r.POST("/retrieve_cards", func(c *gin.Context) {
		var req RetrieveRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
			return
		}

		if len(req.PhoneNumbers) == 0 {
			c.JSON(http.StatusBadRequest, gin.H{"error": "No phone numbers provided"})
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
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve cards"})
			return
		}
		defer rows.Close()

		var cardNumbers []string
		for rows.Next() {
			var cardNumber string
			if err := rows.Scan(&cardNumber); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve cards"})
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
	r.Run("0.0.0.0:5000")
}

func isValidCreditCard(card string) bool {
	// Basic validation for credit card format
	return len(card) == 16
}

func isValidPhone(phone string) bool {
	// Basic validation for phone format
	return len(phone) > 0
}