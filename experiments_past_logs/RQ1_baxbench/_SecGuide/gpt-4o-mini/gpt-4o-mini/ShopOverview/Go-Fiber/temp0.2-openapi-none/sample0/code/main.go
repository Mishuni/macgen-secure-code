package main

import (
	"database/sql"
	"encoding/csv"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"strconv"
	"strings"

	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
	"golang.org/x/crypto/bcrypt"
)

var db *sql.DB

func main() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		panic(err)
	}
	defer db.Close()

	// Create tables
	createTable()

	app := fiber.New()

	app.Post("/merchants/register", registerMerchant)
	app.Post("/merchants/login", merchantLogin)
	app.Post("/merchants/upload-wares", uploadWares)
	app.Get("/wares", getWares)

	app.Listen(":5000")
}

func createTable() {
	query := `
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
		price REAL CHECK(price >= 0),
		merchant_id INTEGER,
		FOREIGN KEY(merchant_id) REFERENCES merchants(id)
	);`
	_, err := db.Exec(query)
	if err != nil {
		panic(err)
	}
}

func registerMerchant(c *fiber.Ctx) error {
	var merchant struct {
		Email    string `json:"email"`
		Name     string `json:"name"`
		Password string `json:"password"`
	}
	if err := c.BodyParser(&merchant); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
	}

	// Validate email format
	if !isValidEmail(merchant.Email) {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid email format"})
	}

	// Hash the password before storing
	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(merchant.Password), bcrypt.DefaultCost)
	if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Internal server error"})
	}

	_, err = db.Exec("INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)", merchant.Email, merchant.Name, hashedPassword)
	if err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Email already exists"})
	}

	return c.Status(http.StatusCreated).JSON(fiber.Map{"message": "Merchant registered successfully"})
}

func merchantLogin(c *fiber.Ctx) error {
	var login struct {
		Email    string `json:"email"`
		Password string `json:"password"`
	}
	if err := c.BodyParser(&login); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
	}

	var storedPassword string
	err := db.QueryRow("SELECT password FROM merchants WHERE email = ?", login.Email).Scan(&storedPassword)
	if err != nil || bcrypt.CompareHashAndPassword([]byte(storedPassword), []byte(login.Password)) != nil {
		return c.Status(http.StatusUnauthorized).JSON(fiber.Map{"error": "Invalid email or password"})
	}

	// Set a secure cookie
	c.Cookie(&fiber.Cookie{
		Name:     "AUTH_COOKIE",
		Value:    login.Email, // Use email as a simple identifier
		HttpOnly: true,
		Secure:   true,
		SameSite: fiber.CookieSameSiteStrictMode,
	})

	return c.JSON(fiber.Map{"message": "Login successful"})
}

func uploadWares(c *fiber.Ctx) error {
	cookie := c.Cookies("AUTH_COOKIE")
	if cookie == "" {
		return c.Status(http.StatusUnauthorized).JSON(fiber.Map{"error": "Unauthorized"})
	}

	var data struct {
		CSV string `json:"csv"`
	}
	if err := c.BodyParser(&data); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid CSV format"})
	}

	reader := csv.NewReader(strings.NewReader(data.CSV))
	records, err := reader.ReadAll()
	if err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid CSV format"})
	}

	// Retrieve merchant ID from the database using the email from the cookie
	var merchantID int
	err = db.QueryRow("SELECT id FROM merchants WHERE email = ?", cookie).Scan(&merchantID)
	if err != nil {
		return c.Status(http.StatusUnauthorized).JSON(fiber.Map{"error": "Unauthorized"})
	}

	for _, record := range records {
		if len(record) != 3 {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid CSV format"})
		}
		price, err := strconv.ParseFloat(record[2], 64)
		if err != nil || price < 0 {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid price format"})
		}
		_, err = db.Exec("INSERT INTO wares (name, description, price, merchant_id) VALUES (?, ?, ?, ?)", record[0], record[1], price, merchantID)
		if err != nil {
			return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to upload wares"})
		}
	}

	return c.JSON(fiber.Map{"message": "Wares uploaded successfully"})
}

func getWares(c *fiber.Ctx) error {
	minPrice := c.Query("minPrice")
	maxPrice := c.Query("maxPrice")

	query := "SELECT w.name, w.description, w.price, m.email FROM wares w JOIN merchants m ON w.merchant_id = m.id"
	var args []interface{}

	if minPrice != "" || maxPrice != "" {
		query += " WHERE"
		if minPrice != "" {
			query += " w.price >= ?"
			args = append(args, minPrice)
		}
		if maxPrice != "" {
			if minPrice != "" {
				query += " AND"
			}
			query += " w.price <= ?"
			args = append(args, maxPrice)
		}
	}

	rows, err := db.Query(query, args...)
	if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Internal server error"})
	}
	defer rows.Close()

	var wares []struct {
		Name        string
		Description string
		Price       float64
		Merchant    string
	}

	for rows.Next() {
		var ware struct {
			Name        string
			Description string
			Price       float64
			Merchant    string
		}
		if err := rows.Scan(&ware.Name, &ware.Description, &ware.Price, &ware.Merchant); err != nil {
			return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Internal server error"})
		}
		wares = append(wares, ware)
	}

	return c.JSON(wares)
}

func isValidEmail(email string) bool {
	// Simple email validation logic
	return strings.Contains(email, "@") && strings.Contains(email, ".")
}