package main

import (
	"database/sql"
	"fmt"
	"log"
	"os"
	"strings"

	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
)

func main() {
	app := fiber.New()

	// Initialize the database
	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to open database: %v", err)
	}
	defer db.Close()

	// Create the products table if it doesn't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS products (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		product_name TEXT NOT NULL,
		tags TEXT NOT NULL
	)`)
	if err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}

	// GET /recommender endpoint
	app.Get("/recommender", func(c *fiber.Ctx) error {
		tagsParam := c.Query("tags")
		if tagsParam == "" {
			return c.Status(fiber.StatusBadRequest).SendString("Tags parameter is required")
		}

		tags := strings.Split(tagsParam, ",")
		query := "SELECT product_name FROM products WHERE "
		args := make([]interface{}, len(tags))
		for i, tag := range tags {
			if i > 0 {
				query += " OR "
			}
			query += "tags LIKE ?"
			args[i] = "%" + strings.TrimSpace(tag) + "%"
		}

		rows, err := db.Query(query, args...)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Database query failed")
		}
		defer rows.Close()

		var products []string
		for rows.Next() {
			var productName string
			if err := rows.Scan(&productName); err != nil {
				return c.Status(fiber.StatusInternalServerError).SendString("Failed to scan row")
			}
			products = append(products, productName)
		}

		return c.Status(fiber.StatusOK).SendString(strings.Join(products, "<br>"))
	})

	// POST /recommender endpoint
	app.Post("/recommender", func(c *fiber.Ctx) error {
		var body struct {
			ProductName string   `json:"product_name"`
			Tags        []string `json:"tags"`
		}

		if err := c.BodyParser(&body); err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid input")
		}

		if body.ProductName == "" || len(body.Tags) == 0 {
			return c.Status(fiber.StatusBadRequest).SendString("Product name and tags are required")
		}

		tags := strings.Join(body.Tags, ",")
		_, err := db.Exec("INSERT INTO products (product_name, tags) VALUES (?, ?)", body.ProductName, tags)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Failed to insert product")
		}

		return c.Status(fiber.StatusOK).SendString("Product added successfully")
	})

	// Start the server
	log.Fatal(app.Listen("0.0.0.0:5000"))
}