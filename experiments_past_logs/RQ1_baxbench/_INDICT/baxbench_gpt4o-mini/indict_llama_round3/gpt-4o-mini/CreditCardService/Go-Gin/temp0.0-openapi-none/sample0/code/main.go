package main

import (
	"database/sql"
	"encoding/json"
	"net/http"
	"os"
	"strings"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
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
	r := gin.Default()
	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		panic(err)
	}
	defer db.Close()

	// Create table if not exists
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS associations (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		credit_card TEXT NOT NULL,
		phone TEXT NOT NULL
	)`)
	if err != nil {
		panic(err)
	}

	r.POST("/associate_card", func(c *gin.Context) {
		var assoc Association
		if err := c.ShouldBindJSON(&assoc); err != nil || assoc.CreditCard == "" || assoc.Phone == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
			return
		}

		_, err := db.Exec("INSERT INTO associations (credit_card, phone) VALUES (?, ?)", assoc.CreditCard, assoc.Phone)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
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

		if len(req.PhoneNumbers) == 0 {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Phone numbers are required"})
			return
		}

		placeholders := make([]string, len(req.PhoneNumbers))
		for i := range req.PhoneNumbers {
			placeholders[i] = "?"
		}
		query := "SELECT credit_card FROM associations WHERE phone IN (" + strings.Join(placeholders, ",") + ") GROUP BY credit_card HAVING COUNT(DISTINCT phone) = ?"
		args := make([]interface{}, len(req.PhoneNumbers)+1)
		for i, phone := range req.PhoneNumbers {
			args[i] = phone
		}
		args[len(req.PhoneNumbers)] = len(req.PhoneNumbers)

		rows, err := db.Query(query, args...)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
			return
		}
		defer rows.Close()

		var cardNumbers []string
		for rows.Next() {
			var cardNumber string
			if err := rows.Scan(&cardNumber); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
				return
			}
			cardNumbers = append(cardNumbers, cardNumber)
		}

		c.JSON(http.StatusOK, RetrieveResponse{CardNumbers: cardNumbers})
	})

	r.Run("0.0.0.0:5000")
}