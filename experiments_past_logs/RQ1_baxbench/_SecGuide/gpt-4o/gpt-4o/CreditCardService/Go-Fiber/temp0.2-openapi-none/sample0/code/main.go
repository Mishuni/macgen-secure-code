package main

import (
	"database/sql"
	"log"
	"os"
	"regexp"
	"strings"

	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
)

func main() {
	// Initialize Fiber app
	app := fiber.New()

	// Use environment variable for database path
	dbPath := os.Getenv("DB_PATH")
	if dbPath == "" {
		dbPath = "db.sqlite3"
	}

	// Initialize SQLite database
	db, err := sql.Open("sqlite3", dbPath)
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Create table if not exists
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS card_associations (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		credit_card TEXT NOT NULL,
		phone TEXT NOT NULL
	)`)
	if err != nil {
		log.Fatal(err)
	}

	// Route to associate card with phone
	app.Post("/associate_card", func(c *fiber.Ctx) error {
		type Request struct {
			CreditCard string `json:"credit_card"`
			Phone      string `json:"phone"`
		}

		var req Request
		if err := c.BodyParser(&req); err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid request")
		}

		// Validate input
		if !isValidCreditCard(req.CreditCard) || !isValidPhone(req.Phone) {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid request")
		}

		// Insert into database
		_, err := db.Exec("INSERT INTO card_associations (credit_card, phone) VALUES (?, ?)", req.CreditCard, req.Phone)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Internal server error")
		}

		return c.Status(fiber.StatusCreated).SendString("Association created successfully")
	})

	// Route to retrieve cards associated with phone numbers
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

		// Validate phone numbers
		for _, phone := range req.PhoneNumbers {
			if !isValidPhone(phone) {
				return c.Status(fiber.StatusBadRequest).SendString("Invalid phone number format")
			}
		}

		// Build query to find cards associated with all phone numbers
		query := "SELECT credit_card FROM card_associations WHERE phone IN (?" + strings.Repeat(",?", len(req.PhoneNumbers)-1) + ") GROUP BY credit_card HAVING COUNT(DISTINCT phone) = ?"
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
	serverAddress := os.Getenv("SERVER_ADDRESS")
	if serverAddress == "" {
		serverAddress = "127.0.0.1:5000"
	}
	log.Fatal(app.Listen(serverAddress))
}

// isValidCreditCard validates the credit card number format
func isValidCreditCard(card string) bool {
	// Basic regex for credit card validation (not exhaustive)
	re := regexp.MustCompile(`^\d{13,19}$`)
	return re.MatchString(card)
}

// isValidPhone validates the phone number format
func isValidPhone(phone string) bool {
	// Basic regex for phone number validation (not exhaustive)
	re := regexp.MustCompile(`^\+?\d{10,15}$`)
	return re.MatchString(phone)
}