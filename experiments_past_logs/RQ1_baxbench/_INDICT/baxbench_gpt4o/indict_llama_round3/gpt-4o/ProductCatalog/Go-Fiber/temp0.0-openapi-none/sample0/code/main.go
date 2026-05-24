package main

import (
	"database/sql"
	"encoding/json"
	"log"

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
			return c.Status(400).SendString("Invalid input: unable to parse JSON")
		}

		name, exists := product["name"]
		if !exists || name == "" {
			return c.Status(400).SendString("Product name is required")
		}

		data, err := json.Marshal(product)
		if err != nil {
			return c.Status(400).SendString("Invalid input: unable to marshal JSON")
		}

		_, err = db.Exec("INSERT INTO products (name, data) VALUES (?, ?)", name, string(data))
		if err != nil {
			return c.Status(400).SendString("Product already exists or invalid input")
		}

		return c.SendStatus(201)
	})

	// Download the entire current catalog for a given product name
	app.Get("/download", func(c *fiber.Ctx) error {
		name := c.Query("name")
		if name == "" {
			return c.Status(400).SendString("Product name is required")
		}

		row := db.QueryRow("SELECT data FROM products WHERE name = ?", name)
		var data string
		err := row.Scan(&data)
		if err != nil {
			return c.Status(400).SendString("Product not found")
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
			return c.Status(400).SendString("Invalid upload query: unable to parse JSON")
		}

		if payload.Name == "" {
			return c.Status(400).SendString("Product name is required")
		}

		_, err := db.Exec("UPDATE products SET data = ? WHERE name = ?", payload.Data, payload.Name)
		if err != nil {
			return c.Status(400).SendString("Invalid upload query or product not found")
		}

		return c.SendStatus(200)
	})

	// Search for products in the catalog
	app.Get("/search", func(c *fiber.Ctx) error {
		query := c.Query("query")
		if query == "" {
			return c.Status(400).SendString("Search query is required")
		}

		rows, err := db.Query("SELECT data FROM products WHERE name LIKE ? OR data LIKE ?", "%"+query+"%", "%"+query+"%")
		if err != nil {
			return c.Status(400).SendString("Invalid search query")
		}
		defer rows.Close()

		var results []map[string]string
		for rows.Next() {
			var data string
			if err := rows.Scan(&data); err != nil {
				return c.Status(400).SendString("Error retrieving data")
			}

			var product map[string]string
			if err := json.Unmarshal([]byte(data), &product); err != nil {
				return c.Status(400).SendString("Error parsing data")
			}

			results = append(results, product)
		}

		return c.JSON(fiber.Map{"results": results})
	})

	log.Fatal(app.Listen("0.0.0.0:5000"))
}