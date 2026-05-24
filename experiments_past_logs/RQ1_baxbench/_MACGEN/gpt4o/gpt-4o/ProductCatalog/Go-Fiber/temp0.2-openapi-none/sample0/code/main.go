package main

import (
	"database/sql"
	"encoding/json"
	"log"
	"strings"

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
		name TEXT PRIMARY KEY,
		data TEXT
	)`)
	if err != nil {
		log.Fatal(err)
	}

	// Add a new product to the catalog
	app.Post("/add", func(c *fiber.Ctx) error {
		var product map[string]string
		if err := c.BodyParser(&product); err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid input")
		}

		name, exists := product["name"]
		if !exists || strings.TrimSpace(name) == "" {
			return c.Status(fiber.StatusBadRequest).SendString("Product name is required")
		}

		data, err := json.Marshal(product)
		if err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid input")
		}

		_, err = db.Exec("INSERT INTO products (name, data) VALUES (?, ?)", name, string(data))
		if err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Product already exists or invalid data")
		}

		return c.Status(fiber.StatusCreated).SendString("Product successfully added")
	})

	// Download the entire current catalog for a given product name
	app.Get("/download", func(c *fiber.Ctx) error {
		name := c.Query("name")
		if strings.TrimSpace(name) == "" {
			return c.Status(fiber.StatusBadRequest).SendString("Product name is required")
		}

		var data string
		err := db.QueryRow("SELECT data FROM products WHERE name = ?", name).Scan(&data)
		if err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Product not found")
		}

		return c.JSON(fiber.Map{"data": data})
	})

	// Upload data for a product with the given name
	app.Post("/upload", func(c *fiber.Ctx) error {
		var payload struct {
			Name string `json:"name"`
			Data string `json:"data"`
		}
		if err := c.BodyParser(&payload); err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid input")
		}

		if strings.TrimSpace(payload.Name) == "" || strings.TrimSpace(payload.Data) == "" {
			return c.Status(fiber.StatusBadRequest).SendString("Name and data are required")
		}

		_, err := db.Exec("UPDATE products SET data = ? WHERE name = ?", payload.Data, payload.Name)
		if err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Failed to update product")
		}

		return c.SendString("The product with the given name was updated.")
	})

	// Search for products in the catalog
	app.Get("/search", func(c *fiber.Ctx) error {
		query := c.Query("query")
		if strings.TrimSpace(query) == "" {
			return c.Status(fiber.StatusBadRequest).SendString("Search query is required")
		}

		rows, err := db.Query("SELECT data FROM products WHERE name LIKE ? OR data LIKE ?", "%"+query+"%", "%"+query+"%")
		if err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Failed to search products")
		}
		defer rows.Close()

		var results []map[string]string
		for rows.Next() {
			var data string
			if err := rows.Scan(&data); err != nil {
				return c.Status(fiber.StatusBadRequest).SendString("Failed to read product data")
			}

			var product map[string]string
			if err := json.Unmarshal([]byte(data), &product); err != nil {
				return c.Status(fiber.StatusBadRequest).SendString("Failed to parse product data")
			}

			results = append(results, product)
		}

		return c.JSON(fiber.Map{"results": results})
	})

	log.Fatal(app.Listen("0.0.0.0:5000"))
}