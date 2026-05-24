
package main

import (
	"database/sql"
	"fmt"
	"log"
	"os"
	"strconv"
	"strings"

	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
)

func main() {
	app := fiber.New()

	// Initialize SQLite database
	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Create tables
	createTables(db)

	// Register a new merchant
	app.Post("/merchants/register", func(c *fiber.Ctx) error {
		type Request struct {
			Email    string `json:"email"`
			Name     string `json:"name"`
			Password string `json:"password"`
		}
		var req Request
		if err := c.BodyParser(&req); err != nil {
			return c.Status(400).SendString("Invalid input")
		}

		stmt, err := db.Prepare("INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)")
		if err != nil {
			return c.Status(500).SendString("Internal Server Error")
		}
		defer stmt.Close()

		_, err = stmt.Exec(req.Email, req.Name, req.Password)
		if err != nil {
			return c.Status(400).SendString("Invalid input")
		}

		return c.SendStatus(201)
	})

	// Merchant login
	app.Post("/merchants/login", func(c *fiber.Ctx) error {
		type Request struct {
			Email    string `json:"email"`
			Password string `json:"password"`
		}
		var req Request
		if err := c.BodyParser(&req); err != nil {
			return c.Status(401).JSON(fiber.Map{"error": "Invalid email or password"})
		}

		var id int
		err := db.QueryRow("SELECT id FROM merchants WHERE email = ? AND password = ?", req.Email, req.Password).Scan(&id)
		if err != nil {
			return c.Status(401).JSON(fiber.Map{"error": "Invalid email or password"})
		}

		c.Cookie(&fiber.Cookie{
			Name:     "AUTH_COOKIE",
			Value:    strconv.Itoa(id),
			HttpOnly: true,
			Secure:   true,
		})

		return c.JSON("Login successful")
	})

	// Upload wares
	app.Post("/merchants/upload-wares", func(c *fiber.Ctx) error {
		type Request struct {
			CSV string `json:"csv"`
		}
		var req Request
		if err := c.BodyParser(&req); err != nil {
			return c.Status(400).SendString("Invalid CSV format")
		}

		authCookie := c.Cookies("AUTH_COOKIE")
		if authCookie == "" {
			return c.Status(401).SendString("Unauthorized")
		}

		merchantID, err := strconv.Atoi(authCookie)
		if err != nil {
			return c.Status(401).SendString("Unauthorized")
		}

		rows := strings.Split(req.CSV, "\n")
		for _, row := range rows {
			columns := strings.Split(row, ",")
			if len(columns) != 3 {
				return c.Status(400).SendString("Invalid CSV format")
			}
			name, description, price := columns[0], columns[1], columns[2]
			stmt, err := db.Prepare("INSERT INTO wares (name, description, price, merchant_id) VALUES (?, ?, ?, ?)")
			if err != nil {
				return c.Status(500).SendString("Internal Server Error")
			}
			defer stmt.Close()

			_, err = stmt.Exec(name, description, price, merchantID)
			if err != nil {
				return c.Status(400).SendString("Invalid CSV format")
			}
		}

		return c.SendStatus(200)
	})

	// Retrieve wares
	app.Get("/wares", func(c *fiber.Ctx) error {
		authCookie := c.Cookies("AUTH_COOKIE")
		if authCookie == "" {
			return c.Status(401).SendString("Unauthorized")
		}

		minPrice := c.Query("minPrice")
		if minPrice != "" {
			if _, err := strconv.ParseFloat(minPrice, 64); err != nil {
				return c.Status(400).SendString("Invalid minPrice")
			}
		}

		maxPrice := c.Query("maxPrice")
		if maxPrice != "" {
			if _, err := strconv.ParseFloat(maxPrice, 64); err != nil {
				return c.Status(400).SendString("Invalid maxPrice")
			}
		}

		query := "SELECT wares.name, wares.description, wares.price, merchants.email FROM wares JOIN merchants ON wares.merchant_id = merchants.id WHERE 1=1"
		if minPrice != "" {
			query += " AND wares.price >= " + minPrice
		}
		if maxPrice != "" {
			query += " AND wares.price <= " + maxPrice
		}

		rows, err := db.Query(query)
		if err != nil {
			return c.Status(500).SendString("Internal Server Error")
		}
		defer rows.Close()

		var html string
		html += "<table><tr><th>Name</th><th>Description</th><th>Price</th><th>Merchant Email</th></tr>"
		for rows.Next() {
			var name, description, email string
			var price float64
			if err := rows.Scan(&name, &description, &price, &email); err != nil {
				return c.Status(500).SendString("Internal Server Error")
			}
			html += fmt.Sprintf("<tr><td>%s</td><td>%s</td><td>%.2f</td><td>%s</td></tr>", name, description, price, email)
		}
		html += "</table>"

		return c.SendString(html)
	})

	log.Fatal(app.Listen("0.0.0.0:5000"))
}

func createTables(db *sql.DB) {
	_, err := db.Exec(`
		CREATE TABLE IF NOT EXISTS merchants (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			email TEXT UNIQUE,
			name TEXT,
			password TEXT
		);
		CREATE TABLE IF NOT EXISTS wares (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			name TEXT,
			description TEXT,
			price REAL,
			merchant_id INTEGER,
			FOREIGN KEY (merchant_id) REFERENCES merchants(id)
		);
	`)
	if err != nil {
		log.Fatal(err)
	}
}