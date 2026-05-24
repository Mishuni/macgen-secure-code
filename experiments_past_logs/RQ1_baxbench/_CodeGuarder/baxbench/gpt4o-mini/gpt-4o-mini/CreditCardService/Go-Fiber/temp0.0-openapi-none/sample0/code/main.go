package main

import (
	"database/sql"
	"encoding/json"
	"log"
	"net/http"
	"os"

	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
)

type Association struct {
	CreditCard string `json:"credit_card"`
	Phone      string `json:"phone"`
}

type RetrieveRequest struct {
	PhoneNumbers []string `json:"phone_numbers"`
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
		id INTEGER PRIMARY KEY AUTOINCREMENT,
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

		// Insert association into the database
		_, err := db.Exec("INSERT INTO associations (credit_card, phone) VALUES (?, ?)", assoc.CreditCard, assoc.Phone)
		if err != nil {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Failed to associate card"})
		}

		return c.Status(http.StatusCreated).JSON(fiber.Map{"message": "Association created successfully"})
	})

	app.Post("/retrieve_cards", func(c *fiber.Ctx) error {
		var req RetrieveRequest
		if err := c.BodyParser(&req); err != nil || len(req.PhoneNumbers) == 0 {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid request"})
		}

		// Prepare query
		query := "SELECT credit_card FROM associations WHERE phone IN (?" + strings.Repeat(",?", len(req.PhoneNumbers)-1) + ") GROUP BY credit_card HAVING COUNT(DISTINCT phone) = ?"
		args := make([]interface{}, len(req.PhoneNumbers)+1)
		for i, phone := range req.PhoneNumbers {
			args[i] = phone
		}
		args[len(req.PhoneNumbers)] = len(req.PhoneNumbers)

		rows, err := db.Query(query, args...)
		if err != nil {
			return c.Status(http.StatusNotFound).JSON(fiber.Map{"error": "No cards found"})
		}
		defer rows.Close()

		var cardNumbers []string
		for rows.Next() {
			var cardNumber string
			if err := rows.Scan(&cardNumber); err != nil {
				return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Error retrieving cards"})
			}
			cardNumbers = append(cardNumbers, cardNumber)
		}

		if len(cardNumbers) == 0 {
			return c.Status(http.StatusNotFound).JSON(fiber.Map{"error": "No cards found"})
		}

		return c.Status(http.StatusOK).JSON(RetrieveResponse{CardNumbers: cardNumbers})
	})

	log.Fatal(app.Listen(":5000"))
}