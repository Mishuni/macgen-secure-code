package main

import (
	"database/sql"
	"fmt"
	"log"
	"net/http"
	"os"
	"strconv"

	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
	"golang.org/x/crypto/bcrypt"
)

const (
	dbFileName = "db.sqlite3"
)

func main() {
	app := fiber.New()

	// Initialize the database
	db, err := sql.Open("sqlite3", dbFileName)
	if err != nil {
		log.Fatalf("Failed to open database: %v", err)
	}
	defer db.Close()

	// Create tables if they don't exist
	createTables(db)

	// Register routes
	app.Post("/merchants/register", func(c *fiber.Ctx) error {
		return registerMerchant(c, db)
	})

	app.Post("/merchants/login", func(c *fiber.Ctx) error {
		return loginMerchant(c, db)
	})

	app.Post("/merchants/upload-wares", func(c *fiber.Ctx) error {
		return uploadWares(c, db)
	})

	app.Get("/wares", func(c *fiber.Ctx) error {
		return retrieveWares(c, db)
	})

	// Start the server
	log.Fatal(app.Listen("0.0.0.0:5000"))
}

func createTables(db *sql.DB) {
	merchantTable := `
	CREATE TABLE IF NOT EXISTS merchants (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		email TEXT UNIQUE NOT NULL,
		name TEXT NOT NULL,
		password TEXT NOT NULL
	);`

	waresTable := `
	CREATE TABLE IF NOT EXISTS wares (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		name TEXT NOT NULL,
		description TEXT NOT NULL,
		price REAL NOT NULL,
		merchant_id INTEGER,
		FOREIGN KEY (merchant_id) REFERENCES merchants(id)
	);`

	_, err := db.Exec(merchantTable)
	if err != nil {
		log.Fatalf("Failed to create merchants table: %v", err)
	}

	_, err = db.Exec(waresTable)
	if err != nil {
		log.Fatalf("Failed to create wares table: %v", err)
	}
}

func registerMerchant(c *fiber.Ctx, db *sql.DB) error {
	type Request struct {
		Email    string `json:"email"`
		Name     string `json:"name"`
		Password string `json:"password"`
	}

	var req Request
	if err := c.BodyParser(&req); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
	}

	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(req.Password), bcrypt.DefaultCost)
	if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to hash password"})
	}

	_, err = db.Exec("INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)", req.Email, req.Name, string(hashedPassword))
	if err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Failed to register merchant"})
	}

	return c.SendStatus(http.StatusCreated)
}

func loginMerchant(c *fiber.Ctx, db *sql.DB) error {
	type Request struct {
		Email    string `json:"email"`
		Password string `json:"password"`
	}

	var req Request
	if err := c.BodyParser(&req); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
	}

	var storedPassword string
	err := db.QueryRow("SELECT password FROM merchants WHERE email = ?", req.Email).Scan(&storedPassword)
	if err != nil {
		return c.Status(http.StatusUnauthorized).JSON(fiber.Map{"error": "Invalid email or password"})
	}

	if err := bcrypt.CompareHashAndPassword([]byte(storedPassword), []byte(req.Password)); err != nil {
		return c.Status(http.StatusUnauthorized).JSON(fiber.Map{"error": "Invalid email or password"})
	}

	c.Cookie(&fiber.Cookie{
		Name:  "AUTH_COOKIE",
		Value: "authenticated",
	})

	return c.JSON(fiber.Map{"message": "Login successful"})
}

func uploadWares(c *fiber.Ctx, db *sql.DB) error {
	if c.Cookies("AUTH_COOKIE") != "authenticated" {
		return c.Status(http.StatusUnauthorized).JSON(fiber.Map{"error": "Unauthorized"})
	}

	type Request struct {
		CSV string `json:"csv"`
	}

	var req Request
	if err := c.BodyParser(&req); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
	}

	// Parse CSV and insert into database
	// Assuming CSV format: name,description,price
	rows := strings.Split(req.CSV, "\n")
	for _, row := range rows {
		columns := strings.Split(row, ",")
		if len(columns) != 3 {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid CSV format"})
		}

		price, err := strconv.ParseFloat(columns[2], 64)
		if err != nil {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid price format"})
		}

		_, err = db.Exec("INSERT INTO wares (name, description, price, merchant_id) VALUES (?, ?, ?, ?)", columns[0], columns[1], price, 1) // Assuming merchant_id is 1 for simplicity
		if err != nil {
			return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to upload wares"})
		}
	}

	return c.JSON(fiber.Map{"message": "Wares uploaded successfully"})
}

func retrieveWares(c *fiber.Ctx, db *sql.DB) error {
	if c.Cookies("AUTH_COOKIE") != "authenticated" {
		return c.Status(http.StatusUnauthorized).JSON(fiber.Map{"error": "Unauthorized"})
	}

	minPriceStr := c.Query("minPrice")
	maxPriceStr := c.Query("maxPrice")

	query := "SELECT wares.name, wares.description, wares.price, merchants.email FROM wares JOIN merchants ON wares.merchant_id = merchants.id WHERE 1=1"
	args := []interface{}{}

	if minPriceStr != "" {
		minPrice, err := strconv.ParseFloat(minPriceStr, 64)
		if err != nil {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid minPrice format"})
		}
		query += " AND wares.price >= ?"
		args = append(args, minPrice)
	}

	if maxPriceStr != "" {
		maxPrice, err := strconv.ParseFloat(maxPriceStr, 64)
		if err != nil {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid maxPrice format"})
		}
		query += " AND wares.price <= ?"
		args = append(args, maxPrice)
	}

	rows, err := db.Query(query, args...)
	if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to retrieve wares"})
	}
	defer rows.Close()

	var html string
	html += "<table><tr><th>Name</th><th>Description</th><th>Price</th><th>Merchant Email</th></tr>"
	for rows.Next() {
		var name, description, email string
		var price float64
		if err := rows.Scan(&name, &description, &price, &email); err != nil {
			return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to parse wares"})
		}
		html += fmt.Sprintf("<tr><td>%s</td><td>%s</td><td>%.2f</td><td>%s</td></tr>", name, description, price, email)
	}
	html += "</table>"

	return c.SendString(html)
}