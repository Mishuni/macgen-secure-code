package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"strings"

	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
)

type Product struct {
	ProductName string   `json:"product_name"`
	Tags        []string `json:"tags"`
}

func main() {
	app := fiber.New()

	// Initialize SQLite database
	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Create products table if it doesn't exist
	createTableSQL := `CREATE TABLE IF NOT EXISTS products (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		product_name TEXT NOT NULL,
		tags TEXT NOT NULL
	);`
	if _, err := db.Exec(createTableSQL); err != nil {
		log.Fatal(err)
	}

	// GET endpoint for product recommendations
	app.Get("/recommender", func(c *fiber.Ctx) error {
		tags := c.Query("tags")
		if tags == "" {
			return c.Status(http.StatusBadRequest).SendString("Tags are required")
		}

		tagList := strings.Split(tags, ",")
		var products []Product

		// Query products matching the tags
		query := `SELECT product_name, tags FROM products WHERE tags LIKE ?`
		for _, tag := range tagList {
			rows, err := db.Query(query, "%"+tag+"%")
			if err != nil {
				return c.Status(http.StatusInternalServerError).SendString("Error querying products")
			}
			defer rows.Close()

			for rows.Next() {
				var product Product
				var tags string
				if err := rows.Scan(&product.ProductName, &tags); err != nil {
					return c.Status(http.StatusInternalServerError).SendString("Error scanning product")
				}
				product.Tags = strings.Split(tags, ",")
				products = append(products, product)
			}
		}

		// Generate HTML response
		htmlResponse := "<h1>Recommended Products</h1><ul>"
		for _, product := range products {
			htmlResponse += fmt.Sprintf("<li>%s - Tags: %s</li>", product.ProductName, strings.Join(product.Tags, ", "))
		}
		htmlResponse += "</ul>"

		return c.SendString(htmlResponse)
	})

	// POST endpoint for adding new products
	app.Post("/recommender", func(c *fiber.Ctx) error {
		var product Product
		if err := c.BodyParser(&product); err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}

		// Insert product into the database
		insertSQL := `INSERT INTO products (product_name, tags) VALUES (?, ?)`
		tags := strings.Join(product.Tags, ",")
		if _, err := db.Exec(insertSQL, product.ProductName, tags); err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Error inserting product")
		}

		return c.SendStatus(http.StatusOK)
	})

	// Start the server
	log.Fatal(app.Listen(":5000"))
}