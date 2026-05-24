package main

import (
	"database/sql"
	"encoding/csv"
	"fmt"
	"net/http"
	"strings"

	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
)

type Merchant struct {
	Email    string `json:"email"`
	Name     string `json:"name"`
	Password string `json:"password"`
}

type WaresUpload struct {
	CSV string `json:"csv"`
}

type Ware struct {
	Name        string  `json:"name"`
	Description string  `json:"description"`
	Price       float64 `json:"price"`
	MerchantEmail string `json:"merchant_email"`
}

var db *sql.DB

func main() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		panic(err)
	}
	defer db.Close()

	// Create tables
	createTable := `
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
		merchant_email TEXT,
		FOREIGN KEY(merchant_email) REFERENCES merchants(email)
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
	err := db.QueryRow("SELECT email, name FROM merchants WHERE email = ? AND password = ?", merchant.Email, merchant.Password).Scan(&dbMerchant.Email, &dbMerchant.Name)
	if err != nil {
		return c.Status(http.StatusUnauthorized).JSON(fiber.Map{"error": "Invalid email or password"})
	}

	return c.JSON(fiber.Map{"message": "Login successful"})
}

func uploadWares(c *fiber.Ctx) error {
	var waresUpload WaresUpload
	if err := c.BodyParser(&waresUpload); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
	}

	// For demonstration, we will use a static merchant email.
	// In a real application, this should be retrieved from the authenticated session.
	merchantEmail := "merchant@example.com"

	reader := csv.NewReader(strings.NewReader(waresUpload.CSV))
	records, err := reader.ReadAll()
	if err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid CSV format"})
	}

	for _, record := range records {
		if len(record) != 3 {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid CSV format"})
		}
		name := record[0]
		description := record[1]
		price := record[2]

		_, err := db.Exec("INSERT INTO wares (name, description, price, merchant_email) VALUES (?, ?, ?, ?)", name, description, price, merchantEmail)
		if err != nil {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Failed to upload wares"})
		}
	}

	return c.Status(http.StatusOK).JSON(fiber.Map{"message": "Wares uploaded successfully"})
}

func getWares(c *fiber.Ctx) error {
	minPrice := c.Query("minPrice")
	maxPrice := c.Query("maxPrice")

	query := "SELECT name, description, price, merchant_email FROM wares WHERE 1=1"
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
		if err := rows.Scan(&ware.Name, &ware.Description, &ware.Price, &ware.MerchantEmail); err != nil {
			return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Internal server error"})
		}
		wares = append(wares, ware)
	}

	// Render as HTML table
	var html strings.Builder
	html.WriteString("<table><tr><th>Name</th><th>Description</th><th>Price</th><th>Merchant Email</th></tr>")
	for _, ware := range wares {
		html.WriteString(fmt.Sprintf("<tr><td>%s</td><td>%s</td><td>%.2f</td><td>%s</td></tr>", ware.Name, ware.Description, ware.Price, ware.MerchantEmail))
	}
	html.WriteString("</table>")

	return c.SendString(html.String())
}