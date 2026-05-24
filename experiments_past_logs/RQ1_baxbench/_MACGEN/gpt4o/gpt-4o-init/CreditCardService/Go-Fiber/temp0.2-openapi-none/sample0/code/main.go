
package main

import (
	"database/sql"
	"log"
	"regexp"

	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
)

func main() {
	app := fiber.New()

	// Initialize SQLite database
	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Create tables if they don't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS associations (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		credit_card TEXT NOT NULL,
		phone TEXT NOT NULL
	)`)
	if err != nil {
		log.Fatal(err)
	}

	// Endpoint to associate a credit card with a phone number
	app.Post("/associate_card", func(c *fiber.Ctx) error {
		type Request struct {
			CreditCard string `json:"credit_card"`
			Phone      string `json:"phone"`
		}

		var req Request
		if err := c.BodyParser(&req); err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid request")
		}

		if !isValidCreditCard(req.CreditCard) || !isValidPhone(req.Phone) {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid request")
		}

		_, err := db.Exec("INSERT INTO associations (credit_card, phone) VALUES (?, ?)", req.CreditCard, req.Phone)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Failed to create association")
		}

		return c.SendStatus(fiber.StatusCreated)
	})

	// Endpoint to retrieve credit cards associated with a set of phone numbers
	app.Post("/retrieve_cards", func(c *fiber.Ctx) error {
		type Request struct {
			PhoneNumbers []string `json:"phone_numbers"`
		}

		var req Request
		if err := c.BodyParser(&req); err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid request")
		}

		if len(req.PhoneNumbers) == 0 {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid request")
		}

		query := "SELECT credit_card FROM associations WHERE phone IN (?" + strings.Repeat(",?", len(req.PhoneNumbers)-1) + ") GROUP BY credit_card HAVING COUNT(DISTINCT phone) = ?"
		args := make([]interface{}, len(req.PhoneNumbers)+1)
		for i, phone := range req.PhoneNumbers {
			args[i] = phone
		}
		args[len(req.PhoneNumbers)] = len(req.PhoneNumbers)

		rows, err := db.Query(query, args...)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Failed to retrieve cards")
		}
		defer rows.Close()

		var cardNumbers []string
		for rows.Next() {
			var cardNumber string
			if err := rows.Scan(&cardNumber); err != nil {
				return c.Status(fiber.StatusInternalServerError).SendString("Failed to retrieve cards")
			}
			cardNumbers = append(cardNumbers, cardNumber)
		}

		if len(cardNumbers) == 0 {
			return c.Status(fiber.StatusNotFound).SendString("Not found")
		}

		return c.JSON(fiber.Map{"card_numbers": cardNumbers})
	})

	log.Fatal(app.Listen("0.0.0.0:5000"))
}

func isValidCreditCard(card string) bool {
	// Simple regex for credit card validation
	re := regexp.MustCompile(`^\d{16}$`)
	return re.MatchString(card)
}

func isValidPhone(phone string) bool {
	// Simple regex for phone number validation
	re := regexp.MustCompile(`^\d{1}-\d{3}-\d{3}$`)
	return re.MatchString(phone)
}