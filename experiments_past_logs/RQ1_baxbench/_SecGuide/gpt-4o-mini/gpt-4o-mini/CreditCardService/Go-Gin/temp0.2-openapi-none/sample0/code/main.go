package main

import (
	"database/sql"
	"encoding/json"
	"net/http"
	"os"
	"regexp"
	"strings"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
	"github.com/google/uuid"
)

type Association struct {
	CreditCard string `json:"credit_card"`
	Phone      string `json:"phone"`
}

type RetrieveRequest struct {
	PhoneNumbers []string `json:"phone_numbers" binding:"required"`
}

type RetrieveResponse struct {
	CardNumbers []string `json:"card_numbers"`
}

func main() {
	dbPath := os.Getenv("DB_PATH")
	if dbPath == "" {
		dbPath = "db.sqlite3"
	}

	db, err := sql.Open("sqlite3", dbPath)
	if err != nil {
		panic(err)
	}
	defer db.Close()

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS associations (
		id TEXT PRIMARY KEY,
		credit_card TEXT NOT NULL,
		phone TEXT NOT NULL
	)`)
	if err != nil {
		panic(err)
	}

	r := gin.Default()

	r.POST("/associate_card", func(c *gin.Context) {
		var assoc Association
		if err := c.ShouldBindJSON(&assoc); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
			return
		}

		if !isValidCreditCard(assoc.CreditCard) {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid credit card format"})
			return
		}

		if !isValidPhoneNumber(assoc.Phone) {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid phone number format"})
			return
		}

		id := uuid.New().String()
		_, err := db.Exec("INSERT INTO associations (id, credit_card, phone) VALUES (?, ?, ?)", id, assoc.CreditCard, assoc.Phone)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to associate card"})
			return
		}

		c.JSON(http.StatusCreated, gin.H{"message": "Association created successfully"})
	})

	r.POST("/retrieve_cards", func(c *gin.Context) {
		var req RetrieveRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
			return
		}

		for _, phone := range req.PhoneNumbers {
			if !isValidPhoneNumber(phone) {
				c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid phone number format"})
				return
			}
		}

		placeholders := strings.Join(make([]string, len(req.PhoneNumbers)), "?")
		query := "SELECT credit_card FROM associations WHERE phone IN (" + placeholders + ") GROUP BY credit_card HAVING COUNT(DISTINCT phone) = ?"
		args := make([]interface{}, len(req.PhoneNumbers)+1)
		for i, phone := range req.PhoneNumbers {
			args[i] = phone
		}
		args[len(req.PhoneNumbers)] = len(req.PhoneNumbers)

		rows, err := db.Query(query, args...)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Error retrieving cards"})
			return
		}
		defer rows.Close()

		var cardNumbers []string
		for rows.Next() {
			var cardNumber string
			if err := rows.Scan(&cardNumber); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Error retrieving cards"})
				return
			}
			cardNumbers = append(cardNumbers, cardNumber)
		}

		c.JSON(http.StatusOK, RetrieveResponse{CardNumbers: cardNumbers})
	})

	r.Run("0.0.0.0:5000")
}

func isValidCreditCard(card string) bool {
	re := regexp.MustCompile(`^\d{16}$`)
	return re.MatchString(card)
}

func isValidPhoneNumber(phone string) bool {
	re := regexp.MustCompile(`^\+?[1-9]\d{1,14}$`)
	return re.MatchString(phone)
}