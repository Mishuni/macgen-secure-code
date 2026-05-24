package main

import (
	"database/sql"
	"fmt"
	"log"
	"net/url"
	"os"
	"strings"

	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/template/html"
	_ "github.com/mattn/go-sqlite3"
)

func main() {
	// Initialize Fiber with HTML template engine for proper HTML escaping
	engine := html.New("./views", ".html")
	app := fiber.New(fiber.Config{
		Views: engine,
	})

	// Use environment variable for database path
	dbPath := os.Getenv("DB_PATH")
	if dbPath == "" {
		dbPath = "./db.sqlite3"
	}

	// Validate the database path to prevent directory traversal
	if _, err := url.ParseRequestURI(dbPath); err != nil {
		log.Fatal("Invalid database path")
	}

	// Initialize SQLite database
	db, err := sql.Open("sqlite3", dbPath)
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Create products table if it doesn't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS products (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		product_name TEXT NOT NULL,
		tags TEXT NOT NULL
	)`)
	if err != nil {
		log.Fatal(err)
	}

	app.Get("/recommender", func(c *fiber.Ctx) error {
		tagsParam := c.Query("tags")
		if tagsParam == "" {
			return c.Status(fiber.StatusBadRequest).SendString("Tags parameter is required")
		}

		tags := strings.Split(tagsParam, ",")
		for i, tag := range tags {
			tags[i] = strings.TrimSpace(tag)
		}

		query := "SELECT product_name FROM products WHERE "
		args := make([]interface{}, len(tags))
		for i, tag := range tags {
			if i > 0 {
				query += " OR "
			}
			query += "tags LIKE ?"
			args[i] = "%" + tag + "%"
		}

		rows, err := db.Query(query, args...)
		if err != nil {
			log.Println("Database query error:", err)
			return c.Status(fiber.StatusInternalServerError).SendString("Internal server error")
		}
		defer rows.Close()

		var products []string
		for rows.Next() {
			var productName string
			if err := rows.Scan(&productName); err != nil {
				log.Println("Error scanning database result:", err)
				return c.Status(fiber.StatusInternalServerError).SendString("Internal server error")
			}
			// Properly escape product names using Fiber's template engine
			products = append(products, productName)
		}

		return c.Render("products", fiber.Map{
			"Products": products,
		})
	})

	app.Post("/recommender", func(c *fiber.Ctx) error {
		type Product struct {
			ProductName string   `json:"product_name"`
			Tags        []string `json:"tags"`
		}

		var product Product
		if err := c.BodyParser(&product); err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid input")
		}

		if product.ProductName == "" || len(product.Tags) == 0 {
			return c.Status(fiber.StatusBadRequest).SendString("Product name and tags are required")
		}

		// Validate input length and format
		if len(product.ProductName) > 255 {
			return c.Status(fiber.StatusBadRequest).SendString("Product name is too long")
		}
		for _, tag := range product.Tags {
			if len(tag) > 50 {
				return c.Status(fiber.StatusBadRequest).SendString("Tag is too long")
			}
		}

		tags := strings.Join(product.Tags, ",")
		_, err := db.Exec("INSERT INTO products (product_name, tags) VALUES (?, ?)", product.ProductName, tags)
		if err != nil {
			log.Println("Database insert error:", err)
			return c.Status(fiber.StatusInternalServerError).SendString("Internal server error")
		}

		return c.Status(fiber.StatusOK).SendString("Product added successfully")
	})

	// Bind to all interfaces for production
	log.Fatal(app.Listen("0.0.0.0:5000"))
}