package main

import (
	"database/sql"
	"encoding/json"
	"log"
	"os"

	"github.com/gofiber/fiber/v2"
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

	// Create products table if it doesn't exist
	_, err = db.Exec(`
		CREATE TABLE IF NOT EXISTS products (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			name TEXT NOT NULL UNIQUE,
			data TEXT NOT NULL
		)
	`)
	if err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}

	// Route to add a new product
	app.Post("/add", func(c *fiber.Ctx) error {
		var product map[string]string
		if err := c.BodyParser(&product); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
		}

		name, exists := product["name"]
		if !exists || name == "" {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Product name is required"})
		}

		data, err := json.Marshal(product)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to process product data"})
		}

		_, err = db.Exec("INSERT INTO products (name, data) VALUES (?, ?)", name, string(data))
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Failed to add product, possibly duplicate name"})
		}

		return c.Status(fiber.StatusCreated).JSON(fiber.Map{"message": "Product successfully added"})
	})

	// Route to download product data
	app.Get("/download", func(c *fiber.Ctx) error {
		name := c.Query("name")
		if name == "" {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Product name is required"})
		}

		var data string
		err := db.QueryRow("SELECT data FROM products WHERE name = ?", name).Scan(&data)
		if err == sql.ErrNoRows {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Product not found"})
		} else if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to retrieve product data"})
		}

		return c.JSON(fiber.Map{"data": data})
	})

	// Route to upload product data
	app.Post("/upload", func(c *fiber.Ctx) error {
		var payload struct {
			Name string `json:"name"`
			Data string `json:"data"`
		}
		if err := c.BodyParser(&payload); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
		}

		if payload.Name == "" || payload.Data == "" {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Both name and data are required"})
		}

		_, err := db.Exec("UPDATE products SET data = ? WHERE name = ?", payload.Data, payload.Name)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to update product data"})
		}

		return c.JSON(fiber.Map{"message": "Product successfully updated"})
	})

	// Route to search for products
	app.Get("/search", func(c *fiber.Ctx) error {
		query := c.Query("query")
		if query == "" {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Search query is required"})
		}

		rows, err := db.Query("SELECT data FROM products WHERE name LIKE ? OR data LIKE ?", "%"+query+"%", "%"+query+"%")
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to search products"})
		}
		defer rows.Close()

		var results []map[string]string
		for rows.Next() {
			var data string
			if err := rows.Scan(&data); err != nil {
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to process search results"})
			}

			var product map[string]string
			if err := json.Unmarshal([]byte(data), &product); err != nil {
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to parse product data"})
			}
			results = append(results, product)
		}

		return c.JSON(fiber.Map{"results": results})
	})

	// Start the server
	log.Println("Server is running on http://0.0.0.0:5000")
	if err := app.Listen("0.0.0.0:5000"); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}