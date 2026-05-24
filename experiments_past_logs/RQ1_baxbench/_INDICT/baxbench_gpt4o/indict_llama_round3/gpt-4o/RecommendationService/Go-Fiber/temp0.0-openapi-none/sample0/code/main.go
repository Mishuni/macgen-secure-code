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

	// Initialize SQLite database
	db, err := sql.Open("sqlite3", "db.sqlite3")
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

	// GET /recommender
	app.Get("/recommender", func(c *fiber.Ctx) error {
		tagsQuery := c.Query("tags")
		if tagsQuery == "" {
			return c.Status(fiber.StatusBadRequest).SendString("Tags query parameter is required")
		}

		tags := strings.Split(tagsQuery, ",")
		query := "SELECT product_name FROM products WHERE "
		args := []interface{}{}

		for i, tag := range tags {
			if i > 0 {
				query += " OR "
			}
			query += "tags LIKE ?"
			args = append(args, "%"+strings.TrimSpace(tag)+"%")
		}

		rows, err := db.Query(query, args...)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Database query error")
		}
		defer rows.Close()

		var products []string
		for rows.Next() {
			var productName string
			if err := rows.Scan(&productName); err != nil {
				return c.Status(fiber.StatusInternalServerError).SendString("Error scanning row")
			}
			products = append(products, productName)
		}

		if len(products) == 0 {
			return c.SendString("No products found")
		}

		htmlResponse := "<ul>"
		for _, product := range products {
			htmlResponse += fmt.Sprintf("<li>%s</li>", product)
		}
		htmlResponse += "</ul>"

		return c.Type("html").SendString(htmlResponse)
	})

	// POST /recommender
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
			return c.Status(fiber.StatusInternalServerError).SendString("Database insert error")
		}

		return c.SendString("Product added successfully")
	})

	log.Fatal(app.Listen("0.0.0.0:5000"))
}