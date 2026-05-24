package main

import (
	"database/sql"
	"encoding/json"
	"net/http"
	"regexp"
	"os"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
)

var db *sql.DB

type AssociateCardRequest struct {
	CreditCard string `json:"credit_card"`
	Phone      string `json:"phone"`
}

type RetrieveCardsRequest struct {
	PhoneNumbers []string `json:"phone_numbers"`
}

type CardResponse struct {
	CardNumbers []string `json:"card_numbers"`
}

func main() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		panic(err)
	}
	defer db.Close()

	// Create table if not exists
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS card_associations (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		credit_card TEXT NOT NULL,
		phone TEXT NOT NULL
	)`)
	if err != nil {
		panic(err)
	}

	router := gin.Default()
	router.POST("/associate_card", associateCard)
	router.POST("/retrieve_cards", retrieveCards)
	router.Run("0.0.0.0:5000")
}

func associateCard(c *gin.Context) {
	var req AssociateCardRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
		return
	}

	if !isValidCreditCard(req.CreditCard) || !isValidPhone(req.Phone) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid credit card or phone number"})
		return
	}

	_, err := db.Exec("INSERT INTO card_associations (credit_card, phone) VALUES (?, ?)", req.CreditCard, req.Phone)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to associate card"})
		return
	}

	c.JSON(http.StatusCreated, gin.H{"message": "Association created successfully"})
}

func retrieveCards(c *gin.Context) {
	var req RetrieveCardsRequest
	if err := c.ShouldBindJSON(&req); err != nil || len(req.PhoneNumbers) == 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
		return
	}

	placeholders := make([]string, len(req.PhoneNumbers))
	for i := range req.PhoneNumbers {
		placeholders[i] = "?"
	}
	query := "SELECT DISTINCT credit_card FROM card_associations WHERE phone IN (" + 
		stringJoin(placeholders, ",") + ") GROUP BY credit_card HAVING COUNT(DISTINCT phone) = ?"

	rows, err := db.Query(query, len(req.PhoneNumbers))
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve cards"})
		return
	}
	defer rows.Close()

	var cardNumbers []string
	for rows.Next() {
		var cardNumber string
		if err := rows.Scan(&cardNumber); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to scan card number"})
			return
		}
		cardNumbers = append(cardNumbers, cardNumber)
	}

	c.JSON(http.StatusOK, CardResponse{CardNumbers: cardNumbers})
}

func isValidCreditCard(card string) bool {
	re := regexp.MustCompile(`^\d{16}$`)
	return re.MatchString(card)
}

func isValidPhone(phone string) bool {
	re := regexp.MustCompile(`^\d{1}-\d{3}-\d{3}$`)
	return re.MatchString(phone)
}

func stringJoin(arr []string, sep string) string {
	result := ""
	for i, s := range arr {
		if i > 0 {
			result += sep
		}
		result += s
	}
	return result
}