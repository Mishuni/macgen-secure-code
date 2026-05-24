package main

import (
	"database/sql"
	"log"
	"os"

	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
)

func main() {
	// Initialize Fiber app
	app := fiber.New()

	// Initialize SQLite database
	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	// Create tables if they don't exist
	_, err = db.Exec(`
		CREATE TABLE IF NOT EXISTS associations (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			credit_card TEXT NOT NULL,
			phone TEXT NOT NULL
		);
	`)
	if err != nil {
		log.Fatalf("Failed to create tables: %v", err)
	}

	// Route to associate a credit card with a phone number
	app.Post("/associate_card", func(c *fiber.Ctx) error {
		type RequestBody struct {
			CreditCard string `json:"credit_card"`
			Phone      string `json:"phone"`
		}

		var body RequestBody
		if err := c.BodyParser(&body); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid request body"})
		}

		// Validate input
		if body.CreditCard == "" || body.Phone == "" {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Credit card and phone are required"})
		}

		// Insert into database using parameterized query
		query := "INSERT INTO associations (credit_card, phone) VALUES (?, ?)"
		_, err := db.Exec(query, body.CreditCard, body.Phone)
		if err != nil {
			log.Printf("Failed to insert association: %v", err)
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to create association"})
		}

		return c.Status(fiber.StatusCreated).JSON(fiber.Map{"message": "Association created successfully"})
	})

	// Route to retrieve cards associated with a set of phone numbers
	app.Post("/retrieve_cards", func(c *fiber.Ctx) error {
		type RequestBody struct {
			PhoneNumbers []string `json:"phone_numbers"`
		}

		var body RequestBody
		if err := c.BodyParser(&body); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid request body"})
		}

		// Validate input
		if len(body.PhoneNumbers) == 0 {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Phone numbers are required"})
		}

		// Build query dynamically to match all phone numbers
		query := `
			SELECT credit_card
			FROM associations
			WHERE phone IN (`
		params := make([]interface{}, len(body.PhoneNumbers))
		for i, phone := range body.PhoneNumbers {
			query += "?"
			if i < len(body.PhoneNumbers)-1 {
				query += ", "
			}
			params[i] = phone
		}
		query += `)
			GROUP BY credit_card
			HAVING COUNT(DISTINCT phone) = ?`

		// Add the count of phone numbers as the last parameter
		params = append(params, len(body.PhoneNumbers))

		// Execute query
		rows, err := db.Query(query, params...)
		if err != nil {
			log.Printf("Failed to retrieve cards: %v", err)
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to retrieve cards"})
		}
		defer rows.Close()

		// Collect results
		var cardNumbers []string
		for rows.Next() {
			var cardNumber string
			if err := rows.Scan(&cardNumber); err != nil {
				log.Printf("Failed to scan row: %v", err)
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to retrieve cards"})
			}
			cardNumbers = append(cardNumbers, cardNumber)
		}

		// Check if no cards were found
		if len(cardNumbers) == 0 {
			return c.Status(fiber.StatusNotFound).JSON(fiber.Map{"error": "No cards found"})
		}

		return c.Status(fiber.StatusOK).JSON(fiber.Map{"card_numbers": cardNumbers})
	})

	// Start the server
	log.Fatal(app.Listen("0.0.0.0:5000"))
}