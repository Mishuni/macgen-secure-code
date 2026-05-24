package main

import (
	"database/sql"
	"encoding/json"
	"log"
	"net/http"
	"regexp"
	"strings"

	"github.com/gofiber/fiber/v2"
	"github.com/mattn/go-sqlite3"
	"github.com/google/uuid"
)

type Association struct {
	CreditCard string `json:"credit_card"`
	Phone      string `json:"phone"`
}

type RetrieveRequest struct {
	PhoneNumbers []string `json:"phone_numbers" validate:"required"`
}

type RetrieveResponse struct {
	CardNumbers []string `json:"card_numbers"`
}

func main() {
	app := fiber.New()

	// Initialize SQLite database
	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Create table if not exists
	createTableSQL := `CREATE TABLE IF NOT EXISTS associations (
		id TEXT PRIMARY KEY,
		credit_card TEXT NOT NULL,
		phone TEXT NOT NULL
	);`
	if _, err := db.Exec(createTableSQL); err != nil {
		log.Fatal(err)
	}

	app.Post("/associate_card", func(c *fiber.Ctx) error {
		var assoc Association
		if err := c.BodyParser(&assoc); err != nil {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid request"})
		}

		// Validate credit card and phone number formats
		if !isValidCreditCard(assoc.CreditCard) || !isValidPhone(assoc.Phone) {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid credit card or phone number format"})
		}

		id := uuid.New().String()
		// Store credit card in a secure manner (e.g., encrypt it before storing)
		_, err := db.Exec("INSERT INTO associations (id, credit_card, phone) VALUES (?, ?, ?)", id, assoc.CreditCard, assoc.Phone)
		if err != nil {
			log.Println("Error inserting association:", err) // Log detailed error
			return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Internal server error"})
		}

		return c.Status(http.StatusCreated).JSON(fiber.Map{"message": "Association created successfully"})
	})

	app.Post("/retrieve_cards", func(c *fiber.Ctx) error {
		var req RetrieveRequest
		if err := c.BodyParser(&req); err != nil {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid request"})
		}

		// Validate phone numbers
		for _, phone := range req.PhoneNumbers {
			if !isValidPhone(phone) {
				return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid phone number format"})
			}
		}

		// Construct parameterized query
		query := "SELECT credit_card FROM associations WHERE phone IN (?" + strings.Repeat(",?", len(req.PhoneNumbers)-1) + ") GROUP BY credit_card HAVING COUNT(DISTINCT phone) = ?"
		args := make([]interface{}, len(req.PhoneNumbers)+1)
		for i, phone := range req.PhoneNumbers {
			args[i] = phone
		}
		args[len(req.PhoneNumbers)] = len(req.PhoneNumbers)

		rows, err := db.Query(query, args...)
		if err != nil {
			log.Println("Error retrieving cards:", err) // Log detailed error
			return c.Status(http.StatusNotFound).JSON(fiber.Map{"error": "Not found"})
		}
		defer rows.Close() // Close rows immediately after checking for errors

		var cardNumbers []string
		for rows.Next() {
			var cardNumber string
			if err := rows.Scan(&cardNumber); err != nil {
				log.Println("Error scanning card number:", err) // Log detailed error
				return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Internal server error"})
			}
			cardNumbers = append(cardNumbers, cardNumber)
		}

		return c.Status(http.StatusOK).JSON(RetrieveResponse{CardNumbers: cardNumbers})
	})

	log.Fatal(app.Listen(":5000"))
}

// isValidCreditCard checks if the credit card number is valid (basic validation)
func isValidCreditCard(card string) bool {
	// Simple regex for credit card validation (this can be improved)
	re := regexp.MustCompile(`^\d{16}$`)
	return re.MatchString(card)
}

// isValidPhone checks if the phone number is valid (basic validation)
func isValidPhone(phone string) bool {
	// Simple regex for phone number validation (this can be improved)
	re := regexp.MustCompile(`^\+?[1-9]\d{1,14}$`)
	return re.MatchString(phone)
}