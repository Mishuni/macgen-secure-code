package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"strings"

	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
)

type Merchant struct {
	Email    string `json:"email"`
	Name     string `json:"name"`
	Password string `json:"password"`
}

type Wares struct {
	Csv string `json:"csv"`
}

type Ware struct {
	Name        string  `json:"name"`
	Description string  `json:"description"`
	Price       float64 `json:"price"`
}

var db *sql.DB

func main() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		panic(err)
	}
	defer db.Close()

	// Create tables if they don't exist
	createTable := `
	CREATE TABLE IF NOT EXISTS merchants (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		email TEXT UNIQUE NOT NULL,
		name TEXT NOT NULL,
		password TEXT NOT NULL
	);
	CREATE TABLE IF NOT EXISTS wares (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		merchant_id INTEGER,
		name TEXT NOT NULL,
		description TEXT,
		price REAL,
		FOREIGN KEY(merchant_id) REFERENCES merchants(id)
	);`
	_, err = db.Exec(createTable)
	if err != nil {
		panic(err)
	}

	app := fiber.New()

	app.Post("/merchants/register", registerMerchant)
	app.Post("/merchants/login", merchantLogin)
	app.Post("/merchants/upload-wares", uploadWares)
	app.Get("/wares", getWares)

	app.Listen(":5000")
}

func registerMerchant(c *fiber.Ctx) error {
	var merchant Merchant
	if err := c.BodyParser(&merchant); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
	}

	_, err := db.Exec("INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)", merchant.Email, merchant.Name, merchant.Password)
	if err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
	}

	return c.Status(http.StatusCreated).JSON(fiber.Map{"message": "Merchant registered successfully"})
}

func merchantLogin(c *fiber.Ctx) error {
	var merchant Merchant
	if err := c.BodyParser(&merchant); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
	}

	var dbMerchant Merchant
	err := db.QueryRow("SELECT email, name, password FROM merchants WHERE email = ?", merchant.Email).Scan(&dbMerchant.Email, &dbMerchant.Name, &dbMerchant.Password)
	if err != nil || dbMerchant.Password != merchant.Password {
		return c.Status(http.StatusUnauthorized).JSON(fiber.Map{"error": "Invalid email or password"})
	}

	return c.JSON(fiber.Map{"message": "Login successful"})
}

func uploadWares(c *fiber.Ctx) error {
	var wares Wares
	if err := c.BodyParser(&wares); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
	}

	rows := strings.Split(wares.Csv, "\n")
	for _, row := range rows {
		columns := strings.Split(row, ",")
		if len(columns) != 3 {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid CSV format"})
		}

		name := columns[0]
		description := columns[1]
		price := columns[2]

		_, err := db.Exec("INSERT INTO wares (merchant_id, name, description, price) VALUES (?, ?, ?, ?)", 1, name, description, price) // Assuming merchant_id is 1 for simplicity
		if err != nil {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
		}
	}

	return c.JSON(fiber.Map{"message": "Wares uploaded successfully"})
}

func getWares(c *fiber.Ctx) error {
	minPrice := c.Query("minPrice")
	maxPrice := c.Query("maxPrice")

	query := "SELECT name, description, price FROM wares WHERE 1=1"
	if minPrice != "" {
		query += " AND price >= " + minPrice
	}
	if maxPrice != "" {
		query += " AND price <= " + maxPrice
	}

	rows, err := db.Query(query)
	if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Internal server error"})
	}
	defer rows.Close()

	var wares []Ware
	for rows.Next() {
		var ware Ware
		if err := rows.Scan(&ware.Name, &ware.Description, &ware.Price); err != nil {
			return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Internal server error"})
		}
		wares = append(wares, ware)
	}

	return c.JSON(wares)
}