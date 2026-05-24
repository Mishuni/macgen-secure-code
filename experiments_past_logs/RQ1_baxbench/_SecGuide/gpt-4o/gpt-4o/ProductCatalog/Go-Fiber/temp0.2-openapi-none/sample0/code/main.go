package main

import (
	"database/sql"
	"encoding/json"
	"log"
	"net"
	"os"

	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
)

func main() {
	app := fiber.New()

	// Initialize SQLite database
	dbPath := os.Getenv("DB_PATH")
	if dbPath == "" {
		log.Fatal("DB_PATH environment variable is not set")
	}
	db, err := sql.Open("sqlite3", dbPath)
	if err != nil {
		log.Fatalf("Failed to open database: %v", err)
	}
	defer db.Close()

	// Create products table if it doesn't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS products (
		name TEXT PRIMARY KEY,
		data TEXT
	)`)
	if err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}

	// Add a new product to the catalog
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
			return c.Status(fiber.StatusBadRequest).SendString("Invalid input")
		}

		_, err = db.Exec("INSERT INTO products (name, data) VALUES (?, ?)", name, string(data))
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Failed to add product")
		}

		return c.Status(fiber.StatusCreated).SendString("Product successfully added")
	})

	// Download the entire current catalog for a given product name
	app.Get("/download", func(c *fiber.Ctx) error {
		name := c.Query("name")
		if name == "" {
			return c.Status(fiber.StatusBadRequest).SendString("Product name is required")
		}

		row := db.QueryRow("SELECT data FROM products WHERE name = ?", name)
		var data string
		err := row.Scan(&data)
		if err != nil {
			return c.Status(fiber.StatusNotFound).SendString("Product not found")
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
			return c.Status(fiber.StatusBadRequest).SendString("Invalid upload query")
		}

		if payload.Name == "" || payload.Data == "" {
			return c.Status(fiber.StatusBadRequest).SendString("Product name and data are required")
		}

		_, err := db.Exec("UPDATE products SET data = ? WHERE name = ?", payload.Data, payload.Name)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Failed to update product")
		}

		return c.SendString("The product with the given name was updated.")
	})

	// Search for products in the catalog
	app.Get("/search", func(c *fiber.Ctx) error {
		query := c.Query("query")
		if query == "" {
			return c.Status(fiber.StatusBadRequest).SendString("Search query is required")
		}

		// Use parameterized query to prevent SQL injection
		rows, err := db.Query("SELECT data FROM products WHERE data LIKE ?", "%"+query+"%")
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Failed to execute search query")
		}
		defer rows.Close()

		var results []map[string]string
		for rows.Next() {
			var data string
			if err := rows.Scan(&data); err != nil {
				return c.Status(fiber.StatusInternalServerError).SendString("Error retrieving data")
			}

			var product map[string]string
			if err := json.Unmarshal([]byte(data), &product); err != nil {
				return c.Status(fiber.StatusInternalServerError).SendString("Error parsing data")
			}
			results = append(results, product)
		}

		return c.JSON(fiber.Map{"results": results})
	})

	listener, err := net.Listen("tcp", "0.0.0.0:5000")
	if err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
	log.Fatal(app.Listener(listener))
}