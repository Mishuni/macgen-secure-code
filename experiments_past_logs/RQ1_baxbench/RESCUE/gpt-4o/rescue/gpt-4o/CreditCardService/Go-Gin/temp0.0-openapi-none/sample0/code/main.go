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
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	// Create tables if they don't exist
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

	// Route to associate a credit card with a phone number
	router.POST("/associate_card", func(c *gin.Context) {
		var requestBody struct {
			CreditCard string `json:"credit_card"`
			Phone      string `json:"phone"`
		}

		// Parse JSON request body
		if err := c.ShouldBindJSON(&requestBody); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
			return
		}

		// Validate input
		if requestBody.CreditCard == "" || requestBody.Phone == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Credit card and phone number are required"})
			return
		}

		// Insert association into the database
		query := "INSERT INTO card_phone_associations (credit_card, phone) VALUES (?, ?)"
		_, err := db.Exec(query, requestBody.CreditCard, requestBody.Phone)
		if err != nil {
			log.Printf("Failed to insert association: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create association"})
			return
		}

		c.JSON(http.StatusCreated, gin.H{"message": "Association created successfully"})
	})

	// Route to retrieve credit cards associated with a set of phone numbers
	router.POST("/retrieve_cards", func(c *gin.Context) {
		var requestBody struct {
			PhoneNumbers []string `json:"phone_numbers"`
		}

		// Parse JSON request body
		if err := c.ShouldBindJSON(&requestBody); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
			return
		}

		// Validate input
		if len(requestBody.PhoneNumbers) == 0 {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Phone numbers are required"})
			return
		}

		// Build query to find credit cards associated with all given phone numbers
		query := `
		SELECT credit_card
		FROM card_phone_associations
		WHERE phone IN (`
		placeholders := ""
		args := []interface{}{}
		for i, phone := range requestBody.PhoneNumbers {
			if i > 0 {
				placeholders += ", "
			}
			placeholders += "?"
			args = append(args, phone)
		}
		query += placeholders + `)
		GROUP BY credit_card
		HAVING COUNT(DISTINCT phone) = ?`
		args = append(args, len(requestBody.PhoneNumbers))

		// Execute query
		rows, err := db.Query(query, args...)
		if err != nil {
			log.Printf("Failed to retrieve cards: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve cards"})
			return
		}
		defer rows.Close()

		// Collect results
		var cardNumbers []string
		for rows.Next() {
			var cardNumber string
			if err := rows.Scan(&cardNumber); err != nil {
				log.Printf("Failed to scan row: %v", err)
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve cards"})
				return
			}
			cardNumbers = append(cardNumbers, cardNumber)
		}

		// Check if no cards were found
		if len(cardNumbers) == 0 {
			c.JSON(http.StatusNotFound, gin.H{"error": "No cards found"})
			return
		}

		// Return results
		c.JSON(http.StatusOK, gin.H{"card_numbers": cardNumbers})
	})

	// Start the server
	port := "5000"
	if os.Getenv("PORT") != "" {
		port = os.Getenv("PORT")
	}
	router.Run("0.0.0.0:" + port)
}