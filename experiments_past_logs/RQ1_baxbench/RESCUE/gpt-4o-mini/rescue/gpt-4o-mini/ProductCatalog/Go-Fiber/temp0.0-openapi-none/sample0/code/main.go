package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/gofiber/fiber/v2"
	"github.com/mattn/go-sqlite3"
	"github.com/google/uuid"
)

type Product struct {
	Name string                 `json:"name"`
	Data map[string]interface{} `json:"data"`
}

func main() {
	app := fiber.New()

	// Initialize SQLite database
	db, err := initDB("db.sqlite3")
	if err != nil {
		log.Fatalf("Could not initialize database: %v", err)
	}
	defer db.Close()

	// Create products table if it doesn't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS products (
		id TEXT PRIMARY KEY,
		name TEXT NOT NULL,
		data TEXT NOT NULL
	)`)
	if err != nil {
		log.Fatalf("Could not create table: %v", err)
	}

	app.Post("/add", func(c *fiber.Ctx) error {
		var product Product
		if err := c.BodyParser(&product); err != nil {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
		}

		if product.Name == "" {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Product name is required"})
		}

		productID := uuid.New().String()
		data, err := json.Marshal(product.Data)
		if err != nil {
			return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Could not marshal data"})
		}

		_, err = db.Exec("INSERT INTO products (id, name, data) VALUES (?, ?, ?)", productID, product.Name, data)
		if err != nil {
			return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Could not add product"})
		}

		return c.Status(http.StatusCreated).JSON(fiber.Map{"message": "Product successfully added"})
	})

	app.Get("/download", func(c *fiber.Ctx) error {
		name := c.Query("name")
		if name == "" {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Product name is required"})
		}

		var product Product
		row := db.QueryRow("SELECT name, data FROM products WHERE name = ?", name)
		var data string
		if err := row.Scan(&product.Name, &data); err != nil {
			return c.Status(http.StatusNotFound).JSON(fiber.Map{"error": "Product not found"})
		}

		if err := json.Unmarshal([]byte(data), &product.Data); err != nil {
			return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Could not unmarshal data"})
		}

		return c.JSON(product)
	})

	app.Post("/upload", func(c *fiber.Ctx) error {
		var product Product
		if err := c.BodyParser(&product); err != nil {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid upload query"})
		}

		if product.Name == "" || product.Data == nil {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Product name and data are required"})
		}

		data, err := json.Marshal(product.Data)
		if err != nil {
			return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Could not marshal data"})
		}

		_, err = db.Exec("REPLACE INTO products (name, data) VALUES (?, ?)", product.Name, data)
		if err != nil {
			return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Could not upload product data"})
		}

		return c.Status(http.StatusOK).JSON(fiber.Map{"message": "Product updated"})
	})

	app.Get("/search", func(c *fiber.Ctx) error {
		query := c.Query("query")
		if query == "" {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Search query is required"})
		}

		rows, err := db.Query("SELECT name, data FROM products WHERE name LIKE ? OR data LIKE ?", "%"+query+"%", "%"+query+"%")
		if err != nil {
			return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Could not search products"})
		}
		defer rows.Close()

		var results []Product
		for rows.Next() {
			var product Product
			var data string
			if err := rows.Scan(&product.Name, &data); err != nil {
				return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Could not scan product"})
			}
			if err := json.Unmarshal([]byte(data), &product.Data); err != nil {
				return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Could not unmarshal data"})
			}
			results = append(results, product)
		}

		return c.JSON(fiber.Map{"results": results})
	})

	log.Fatal(app.Listen(":5000"))
}

func initDB(dbName string) (*sqlite3.SQLiteConn, error) {
	return sqlite3.Open(dbName)
}