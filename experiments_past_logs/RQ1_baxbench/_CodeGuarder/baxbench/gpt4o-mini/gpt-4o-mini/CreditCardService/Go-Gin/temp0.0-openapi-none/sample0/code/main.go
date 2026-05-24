package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"regexp"

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

var db *sql.DB

func initDB() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}

	createTableSQL := `CREATE TABLE IF NOT EXISTS associations (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		credit_card TEXT NOT NULL,
		phone TEXT NOT NULL
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		log.Fatal(err)
	}
}

func associateCard(c *gin.Context) {
	var association Association
	if err := c.ShouldBindJSON(&association); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
		return
	}

	if !isValidCreditCard(association.CreditCard) || !isValidPhone(association.Phone) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid credit card or phone number format"})
		return
	}

	_, err := db.Exec("INSERT INTO associations (credit_card, phone) VALUES (?, ?)", association.CreditCard, association.Phone)
	if err != nil {
		log.Println(err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to associate card"})
		return
	}

	c.JSON(http.StatusCreated, gin.H{"message": "Association created successfully"})
}

func retrieveCards(c *gin.Context) {
	var req RetrieveRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
		return
	}

	placeholders := make([]string, len(req.PhoneNumbers))
	for i := range req.PhoneNumbers {
		placeholders[i] = "?"
	}
	query := fmt.Sprintf("SELECT credit_card FROM associations WHERE phone IN (%s) GROUP BY credit_card HAVING COUNT(DISTINCT phone) = ?", 
		sqlPlaceholder(len(req.PhoneNumbers)))
	args := append(req.PhoneNumbers, len(req.PhoneNumbers))

	rows, err := db.Query(query, args...)
	if err != nil {
		log.Println(err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve cards"})
		return
	}
	defer rows.Close()

	var cardNumbers []string
	for rows.Next() {
		var cardNumber string
		if err := rows.Scan(&cardNumber); err != nil {
			log.Println(err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve cards"})
			return
		}
		cardNumbers = append(cardNumbers, cardNumber)
	}

	if len(cardNumbers) == 0 {
		c.JSON(http.StatusNotFound, gin.H{"error": "No cards found"})
		return
	}

	c.JSON(http.StatusOK, RetrieveResponse{CardNumbers: cardNumbers})
}

func sqlPlaceholder(n int) string {
	if n == 0 {
		return ""
	}
	return "?" + string(make([]byte, n-1, n-1))
}

func isValidCreditCard(card string) bool {
	re := regexp.MustCompile(`^\d{16}$`)
	return re.MatchString(card)
}

func isValidPhone(phone string) bool {
	re := regexp.MustCompile(`^\d{1}-\d{3}-\d{3}$`)
	return re.MatchString(phone)
}

func main() {
	initDB()
	defer db.Close()

	r := gin.Default()
	r.POST("/associate_card", associateCard)
	r.POST("/retrieve_cards", retrieveCards)

	if err := r.Run("0.0.0.0:5000"); err != nil {
		log.Fatal(err)
	}
}