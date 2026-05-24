package main

import (
	"database/sql"
	"encoding/csv"
	"fmt"
	"log"
	"net/http"
	"os"
	"strconv"
	"strings"

	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
	"golang.org/x/crypto/bcrypt"
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
	createTables(db)

	app.Post("/merchants/register", func(c *fiber.Ctx) error {
		var data struct {
			Email    string `json:"email"`
			Name     string `json:"name"`
			Password string `json:"password"`
		}

		if err := c.BodyParser(&data); err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}

		hashedPassword, err := bcrypt.GenerateFromPassword([]byte(data.Password), bcrypt.DefaultCost)
		if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Error processing password")
		}

		_, err = db.Exec("INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)", data.Email, data.Name, string(hashedPassword))
		if err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}

		return c.SendStatus(http.StatusCreated)
	})

	app.Post("/merchants/login", func(c *fiber.Ctx) error {
		var data struct {
			Email    string `json:"email"`
			Password string `json:"password"`
		}

		if err := c.BodyParser(&data); err != nil {
			return c.Status(http.StatusUnauthorized).JSON(fiber.Map{"error": "Invalid email or password"})
		}

		var storedPassword string
		err := db.QueryRow("SELECT password FROM merchants WHERE email = ?", data.Email).Scan(&storedPassword)
		if err != nil || bcrypt.CompareHashAndPassword([]byte(storedPassword), []byte(data.Password)) != nil {
			return c.Status(http.StatusUnauthorized).JSON(fiber.Map{"error": "Invalid email or password"})
		}

		c.Cookie(&fiber.Cookie{
			Name:  "AUTH_COOKIE",
			Value: data.Email,
		})

		return c.JSON("Login successful")
	})

	app.Post("/merchants/upload-wares", func(c *fiber.Ctx) error {
		merchantEmail := c.Cookies("AUTH_COOKIE")
		if merchantEmail == "" {
			return c.Status(http.StatusUnauthorized).SendString("Unauthorized")
		}

		var data struct {
			CSV string `json:"csv"`
		}

		if err := c.BodyParser(&data); err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid CSV format")
		}

		reader := csv.NewReader(strings.NewReader(data.CSV))
		records, err := reader.ReadAll()
		if err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid CSV format")
		}

		for _, record := range records {
			if len(record) != 3 {
				return c.Status(http.StatusBadRequest).SendString("Invalid CSV format")
			}

			price, err := strconv.ParseFloat(record[2], 64)
			if err != nil {
				return c.Status(http.StatusBadRequest).SendString("Invalid CSV format")
			}

			_, err = db.Exec("INSERT INTO wares (name, description, price, merchant_email) VALUES (?, ?, ?, ?)", record[0], record[1], price, merchantEmail)
			if err != nil {
				return c.Status(http.StatusBadRequest).SendString("Invalid CSV format")
			}
		}

		return c.SendString("Wares uploaded successfully")
	})

	app.Get("/wares", func(c *fiber.Ctx) error {
		if c.Cookies("AUTH_COOKIE") == "" {
			return c.Status(http.StatusUnauthorized).SendString("Unauthorized")
		}

		minPrice := c.Query("minPrice")
		maxPrice := c.Query("maxPrice")

		query := "SELECT name, description, price, merchant_email FROM wares WHERE 1=1"
		args := []interface{}{}

		if minPrice != "" {
			query += " AND price >= ?"
			price, err := strconv.ParseFloat(minPrice, 64)
			if err != nil {
				return c.Status(http.StatusBadRequest).SendString("Invalid minPrice")
			}
			args = append(args, price)
		}

		if maxPrice != "" {
			query += " AND price <= ?"
			price, err := strconv.ParseFloat(maxPrice, 64)
			if err != nil {
				return c.Status(http.StatusBadRequest).SendString("Invalid maxPrice")
			}
			args = append(args, price)
		}

		rows, err := db.Query(query, args...)
		if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Error retrieving wares")
		}
		defer rows.Close()

		var html strings.Builder
		html.WriteString("<table><tr><th>Name</th><th>Description</th><th>Price</th><th>Merchant Email</th></tr>")

		for rows.Next() {
			var name, description, merchantEmail string
			var price float64
			if err := rows.Scan(&name, &description, &price, &merchantEmail); err != nil {
				return c.Status(http.StatusInternalServerError).SendString("Error retrieving wares")
			}
			html.WriteString(fmt.Sprintf("<tr><td>%s</td><td>%s</td><td>%.2f</td><td>%s</td></tr>", name, description, price, merchantEmail))
		}

		html.WriteString("</table>")
		return c.Type("html").SendString(html.String())
	})

	log.Fatal(app.Listen("0.0.0.0:5000"))
}

func createTables(db *sql.DB) {
	_, err := db.Exec(`
		CREATE TABLE IF NOT EXISTS merchants (
			email TEXT PRIMARY KEY,
			name TEXT,
			password TEXT
		);
		CREATE TABLE IF NOT EXISTS wares (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			name TEXT,
			description TEXT,
			price REAL,
			merchant_email TEXT,
			FOREIGN KEY (merchant_email) REFERENCES merchants(email)
		);
	`)
	if err != nil {
		log.Fatal(err)
	}
}