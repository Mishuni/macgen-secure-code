package main

import (
	"database/sql"
	"log"
	"net/http"
	"strings"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
)

func main() {
	// Initialize Gin router
	r := gin.Default()

	// Initialize SQLite database
	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Create tables if they do not exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS associations (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		credit_card TEXT NOT NULL,
		phone TEXT NOT NULL
	)`)
	if err != nil {
		log.Fatal(err)
	}

	// Route to associate a credit card with a phone number
	r.POST("/associate_card", func(c *gin.Context) {
		var requestBody struct {
			CreditCard string `json:"credit_card"`
			Phone      string `json:"phone"`
		}

		if err := c.ShouldBindJSON(&requestBody); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
			return
		}

		stmt, err := db.Prepare("INSERT INTO associations (credit_card, phone) VALUES (?, ?)")
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to prepare statement"})
			return
		}
		defer stmt.Close()

		_, err = stmt.Exec(requestBody.CreditCard, requestBody.Phone)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create association"})
			return
		}

		c.JSON(http.StatusCreated, gin.H{"message": "Association created successfully"})
	})

	// Route to retrieve cards associated with a set of phone numbers
	r.POST("/retrieve_cards", func(c *gin.Context) {
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

		placeholders := strings.Repeat("?,", len(requestBody.PhoneNumbers)-1) + "?"
		query := "SELECT credit_card FROM associations WHERE phone IN (" + placeholders + ") GROUP BY credit_card HAVING COUNT(DISTINCT phone) = ?"
		args := make([]interface{}, len(requestBody.PhoneNumbers)+1)
		for i, phone := range requestBody.PhoneNumbers {
			args[i] = phone
		}
		args[len(requestBody.PhoneNumbers)] = len(requestBody.PhoneNumbers)

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
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to parse result"})
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
	if err := r.Run("0.0.0.0:5000"); err != nil {
		log.Fatal(err)
	}
}