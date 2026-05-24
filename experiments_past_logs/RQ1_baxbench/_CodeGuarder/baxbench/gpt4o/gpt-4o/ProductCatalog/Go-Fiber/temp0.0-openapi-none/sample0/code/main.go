package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"os"

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

	// Create products table if it doesn't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS products (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		name TEXT NOT NULL UNIQUE,
		data TEXT NOT NULL
	)`)
	if err != nil {
		log.Fatal(err)
	}

	// Add product endpoint
	app.Post("/add", func(c *fiber.Ctx) error {
		var product map[string]string
		if err := c.BodyParser(&product); err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid input")
		}

		name, exists := product["name"]
		if !exists || name == "" {
			return c.Status(fiber.StatusBadRequest).SendString("Product name is required")
		}

		data, err := json.Marshal(product)
		if err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid product data")
		}

		_, err = db.Exec("INSERT INTO products (name, data) VALUES (?, ?)", name, string(data))
		if err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Product already exists or invalid data")
		}

		return c.Status(fiber.StatusCreated).SendString("Product successfully added")
	})

	// Download catalog endpoint
	app.Get("/download", func(c *fiber.Ctx) error {
		name := c.Query("name")
		if name == "" {
			return c.Status(fiber.StatusBadRequest).SendString("Product name is required")
		}

		var data string
		err := db.QueryRow("SELECT data FROM products WHERE name = ?", name).Scan(&data)
		if err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Product not found")
		}

		return c.JSON(fiber.Map{"data": data})
	})

	// Upload product data endpoint
	app.Post("/upload", func(c *fiber.Ctx) error {
		var product map[string]string
		if err := c.BodyParser(&product); err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid input")
		}

		name, nameExists := product["name"]
		data, dataExists := product["data"]
		if !nameExists || !dataExists || name == "" || data == "" {
			return c.Status(fiber.StatusBadRequest).SendString("Product name and data are required")
		}

		_, err := db.Exec("UPDATE products SET data = ? WHERE name = ?", data, name)
		if err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Product not found or invalid data")
		}

		return c.SendString("Product successfully updated")
	})

	// Search products endpoint
	app.Get("/search", func(c *fiber.Ctx) error {
		query := c.Query("query")
		if query == "" {
			return c.Status(fiber.StatusBadRequest).SendString("Search query is required")
		}

		rows, err := db.Query("SELECT data FROM products WHERE name LIKE ? OR data LIKE ?", "%"+query+"%", "%"+query+"%")
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Error searching products")
		}
		defer rows.Close()

		var results []map[string]string
		for rows.Next() {
			var data string
			if err := rows.Scan(&data); err != nil {
				return c.Status(fiber.StatusInternalServerError).SendString("Error reading product data")
			}

			var product map[string]string
			if err := json.Unmarshal([]byte(data), &product); err != nil {
				return c.Status(fiber.StatusInternalServerError).SendString("Error parsing product data")
			}

			results = append(results, product)
		}

		return c.JSON(fiber.Map{"results": results})
	})

	// Start server
	log.Fatal(app.Listen("0.0.0.0:5000"))
}