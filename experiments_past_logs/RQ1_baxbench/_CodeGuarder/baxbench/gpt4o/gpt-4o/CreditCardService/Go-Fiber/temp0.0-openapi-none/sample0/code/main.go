package main

import (
	"database/sql"
	"fmt"
	"log"
	"os"
	"strings"

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

	// Create tables if they do not exist
	createTables(db)

	// Define routes
	app.Post("/associate_card", func(c *fiber.Ctx) error {
		type Request struct {
			CreditCard string `json:"credit_card"`
			Phone      string `json:"phone"`
		}

		var req Request
		if err := c.BodyParser(&req); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid request"})
		}

		if err := validateCreditCard(req.CreditCard); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": err.Error()})
		}

		if err := validatePhone(req.Phone); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": err.Error()})
		}

		_, err := db.Exec("INSERT INTO card_associations (credit_card, phone) VALUES (?, ?)", req.CreditCard, req.Phone)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to associate card"})
		}

		return c.Status(fiber.StatusCreated).JSON(fiber.Map{"message": "Association created successfully"})
	})

	app.Post("/retrieve_cards", func(c *fiber.Ctx) error {
		type Request struct {
			PhoneNumbers []string `json:"phone_numbers"`
		}

		var req Request
		if err := c.BodyParser(&req); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid request"})
		}

		if len(req.PhoneNumbers) == 0 {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Phone numbers are required"})
		}

		placeholders := strings.Repeat("?,", len(req.PhoneNumbers)-1) + "?"
		query := fmt.Sprintf("SELECT credit_card FROM card_associations WHERE phone IN (%s) GROUP BY credit_card HAVING COUNT(DISTINCT phone) = ?", placeholders)

		args := make([]interface{}, len(req.PhoneNumbers)+1)
		for i, phone := range req.PhoneNumbers {
			args[i] = phone
		}
		args[len(req.PhoneNumbers)] = len(req.PhoneNumbers)

		rows, err := db.Query(query, args...)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to retrieve cards"})
		}
		defer rows.Close()

		var cardNumbers []string
		for rows.Next() {
			var cardNumber string
			if err := rows.Scan(&cardNumber); err != nil {
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to retrieve cards"})
			}
			cardNumbers = append(cardNumbers, cardNumber)
		}

		if len(cardNumbers) == 0 {
			return c.Status(fiber.StatusNotFound).JSON(fiber.Map{"error": "No cards found"})
		}

		return c.JSON(fiber.Map{"card_numbers": cardNumbers})
	})

	log.Fatal(app.Listen("0.0.0.0:5000"))
}

func createTables(db *sql.DB) {
	createTableSQL := `
	CREATE TABLE IF NOT EXISTS card_associations (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		credit_card TEXT NOT NULL,
		phone TEXT NOT NULL
	);`
	if _, err := db.Exec(createTableSQL); err != nil {
		log.Fatalf("Failed to create tables: %v", err)
	}
}

func validateCreditCard(card string) error {
	if len(card) != 16 {
		return fmt.Errorf("Credit card number must be 16 digits")
	}
	return nil
}

func validatePhone(phone string) error {
	if len(phone) < 7 {
		return fmt.Errorf("Phone number is too short")
	}
	return nil
}