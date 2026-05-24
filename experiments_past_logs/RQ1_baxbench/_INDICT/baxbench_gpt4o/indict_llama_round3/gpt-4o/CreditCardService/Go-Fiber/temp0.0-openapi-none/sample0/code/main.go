package main

import (
	"database/sql"
	"log"
	"strings"

	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
)

func main() {
	// Initialize Fiber app
	app := fiber.New()

	// Initialize SQLite database
	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Create tables if they do not exist
	_, err = db.Exec(`
		CREATE TABLE IF NOT EXISTS associations (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			credit_card TEXT NOT NULL,
			phone TEXT NOT NULL
		);
	`)
	if err != nil {
		log.Fatal(err)
	}

	// Route to associate a credit card with a phone number
	app.Post("/associate_card", func(c *fiber.Ctx) error {
		type Request struct {
			CreditCard string `json:"credit_card"`
			Phone      string `json:"phone"`
		}

		var req Request
		if err := c.BodyParser(&req); err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid request")
		}

		if req.CreditCard == "" || req.Phone == "" {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid request")
		}

		_, err := db.Exec("INSERT INTO associations (credit_card, phone) VALUES (?, ?)", req.CreditCard, req.Phone)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Internal server error")
		}

		return c.SendStatus(fiber.StatusCreated)
	})

	// Route to retrieve cards associated with a set of phone numbers
	app.Post("/retrieve_cards", func(c *fiber.Ctx) error {
		type Request struct {
			PhoneNumbers []string `json:"phone_numbers"`
		}

		type Response struct {
			CardNumbers []string `json:"card_numbers"`
		}

		var req Request
		if err := c.BodyParser(&req); err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid request")
		}

		if len(req.PhoneNumbers) == 0 {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid request")
		}

		placeholders := strings.Repeat("?,", len(req.PhoneNumbers))
		placeholders = placeholders[:len(placeholders)-1] // Remove trailing comma

		query := `
			SELECT credit_card FROM associations
			WHERE phone IN (` + placeholders + `)
			GROUP BY credit_card
			HAVING COUNT(DISTINCT phone) = ?
		`

		args := make([]interface{}, len(req.PhoneNumbers)+1)
		for i, phone := range req.PhoneNumbers {
			args[i] = phone
		}
		args[len(req.PhoneNumbers)] = len(req.PhoneNumbers)

		rows, err := db.Query(query, args...)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Internal server error")
		}
		defer rows.Close()

		var cardNumbers []string
		for rows.Next() {
			var cardNumber string
			if err := rows.Scan(&cardNumber); err != nil {
				return c.Status(fiber.StatusInternalServerError).SendString("Internal server error")
			}
			cardNumbers = append(cardNumbers, cardNumber)
		}

		if len(cardNumbers) == 0 {
			return c.Status(fiber.StatusNotFound).SendString("Not found")
		}

		return c.JSON(Response{CardNumbers: cardNumbers})
	})

	// Start server
	log.Fatal(app.Listen("0.0.0.0:5000"))
}