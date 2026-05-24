package main

import (
	"database/sql"
	"log"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
)

func main() {
	// Initialize Gin router
	router := gin.Default()

	// Initialize SQLite database
	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to open database: %v", err)
	}
	defer db.Close()

	// Create table if not exists
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS card_phone_associations (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		credit_card TEXT NOT NULL,
		phone TEXT NOT NULL
	)`)
	if err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}

	// Define /associate_card endpoint
	router.POST("/associate_card", func(c *gin.Context) {
		var requestBody struct {
			CreditCard string `json:"credit_card" binding:"required"`
			Phone      string `json:"phone" binding:"required"`
		}

		if err := c.ShouldBindJSON(&requestBody); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
			return
		}

		_, err := db.Exec("INSERT INTO card_phone_associations (credit_card, phone) VALUES (?, ?)", requestBody.CreditCard, requestBody.Phone)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to associate card"})
			return
		}

		c.Status(http.StatusCreated)
	})

	// Define /retrieve_cards endpoint
	router.POST("/retrieve_cards", func(c *gin.Context) {
		var requestBody struct {
			PhoneNumbers []string `json:"phone_numbers" binding:"required"`
		}

		if err := c.ShouldBindJSON(&requestBody); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
			return
		}

		if len(requestBody.PhoneNumbers) == 0 {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Phone numbers are required"})
			return
		}

		query := "SELECT credit_card FROM card_phone_associations WHERE phone IN (?" + strings.Repeat(",?", len(requestBody.PhoneNumbers)-1) + ") GROUP BY credit_card HAVING COUNT(DISTINCT phone) = ?"
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
	if err := router.Run("0.0.0.0:5000"); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}