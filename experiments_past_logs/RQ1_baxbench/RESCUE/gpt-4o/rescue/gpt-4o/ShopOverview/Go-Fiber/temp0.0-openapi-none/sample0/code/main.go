package main

import (
	"database/sql"
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"strconv"
	"strings"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
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
	createTables(db)

	// Routes
	app.Post("/merchants/register", func(c *fiber.Ctx) error {
		var body struct {
			Email    string `json:"email"`
			Name     string `json:"name"`
			Password string `json:"password"`
		}

		if err := c.BodyParser(&body); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
		}

		// Validate input
		if body.Email == "" || body.Name == "" || body.Password == "" {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "All fields are required"})
		}

		// Insert merchant into database
		_, err := db.Exec("INSERT INTO merchants (id, email, name, password) VALUES (?, ?, ?, ?)",
			uuid.New().String(), body.Email, body.Name, body.Password)
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Failed to register merchant"})
		}

		return c.Status(fiber.StatusCreated).JSON(fiber.Map{"message": "Merchant registered successfully"})
	})

	app.Post("/merchants/login", func(c *fiber.Ctx) error {
		var body struct {
			Email    string `json:"email"`
			Password string `json:"password"`
		}

		if err := c.BodyParser(&body); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
		}

		// Validate input
		if body.Email == "" || body.Password == "" {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Email and password are required"})
		}

		// Check credentials
		var id string
		err := db.QueryRow("SELECT id FROM merchants WHERE email = ? AND password = ?", body.Email, body.Password).Scan(&id)
		if err != nil {
			return c.Status(fiber.StatusUnauthorized).JSON(fiber.Map{"error": "Invalid email or password"})
		}

		// Set cookie
		c.Cookie(&fiber.Cookie{
			Name:  "AUTH_COOKIE",
			Value: id,
			Path:  "/",
		})

		return c.JSON(fiber.Map{"message": "Login successful"})
	})

	app.Post("/merchants/upload-wares", func(c *fiber.Ctx) error {
		authCookie := c.Cookies("AUTH_COOKIE")
		if authCookie == "" {
			return c.Status(fiber.StatusUnauthorized).JSON(fiber.Map{"error": "Unauthorized"})
		}

		var body struct {
			CSV string `json:"csv"`
		}

		if err := c.BodyParser(&body); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
		}

		// Parse CSV
		reader := csv.NewReader(strings.NewReader(body.CSV))
		records, err := reader.ReadAll()
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid CSV format"})
		}

		// Insert wares into database
		for _, record := range records {
			if len(record) != 3 {
				return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid CSV format"})
			}

			name := record[0]
			description := record[1]
			price, err := strconv.ParseFloat(record[2], 64)
			if err != nil {
				return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid price in CSV"})
			}

			_, err = db.Exec("INSERT INTO wares (id, merchant_id, name, description, price) VALUES (?, ?, ?, ?, ?)",
				uuid.New().String(), authCookie, name, description, price)
			if err != nil {
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to upload wares"})
			}
		}

		return c.JSON(fiber.Map{"message": "Wares uploaded successfully"})
	})

	app.Get("/wares", func(c *fiber.Ctx) error {
		authCookie := c.Cookies("AUTH_COOKIE")
		if authCookie == "" {
			return c.Status(fiber.StatusUnauthorized).JSON(fiber.Map{"error": "Unauthorized"})
		}

		minPrice := c.Query("minPrice")
		maxPrice := c.Query("maxPrice")

		query := "SELECT wares.name, wares.description, wares.price, merchants.email FROM wares JOIN merchants ON wares.merchant_id = merchants.id WHERE 1=1"
		args := []interface{}{}

		if minPrice != "" {
			query += " AND wares.price >= ?"
			price, err := strconv.ParseFloat(minPrice, 64)
			if err != nil {
				return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid minPrice"})
			}
			args = append(args, price)
		}

		if maxPrice != "" {
			query += " AND wares.price <= ?"
			price, err := strconv.ParseFloat(maxPrice, 64)
			if err != nil {
				return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid maxPrice"})
			}
			args = append(args, price)
		}

		rows, err := db.Query(query, args...)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to retrieve wares"})
		}
		defer rows.Close()

		// Generate HTML table
		html := "<table><tr><th>Name</th><th>Description</th><th>Price</th><th>Merchant Email</th></tr>"
		for rows.Next() {
			var name, description, email string
			var price float64
			if err := rows.Scan(&name, &description, &price, &email); err != nil {
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to parse wares"})
			}
			html += fmt.Sprintf("<tr><td>%s</td><td>%s</td><td>%.2f</td><td>%s</td></tr>", name, description, price, email)
		}
		html += "</table>"

		return c.Type("html").SendString(html)
	})

	// Start server
	log.Fatal(app.Listen("0.0.0.0:5000"))
}

func createTables(db *sql.DB) {
	_, err := db.Exec(`
		CREATE TABLE IF NOT EXISTS merchants (
			id TEXT PRIMARY KEY,
			email TEXT UNIQUE NOT NULL,
			name TEXT NOT NULL,
			password TEXT NOT NULL
		);
		CREATE TABLE IF NOT EXISTS wares (
			id TEXT PRIMARY KEY,
			merchant_id TEXT NOT NULL,
			name TEXT NOT NULL,
			description TEXT NOT NULL,
			price REAL NOT NULL,
			FOREIGN KEY (merchant_id) REFERENCES merchants (id)
		);
	`)
	if err != nil {
		log.Fatalf("Failed to create tables: %v", err)
	}
}