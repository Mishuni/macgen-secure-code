package main

import (
	"database/sql"
	"log"
	"os"
	"strings"

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

	// Create tables if they don't exist
	createTableQuery := `
	CREATE TABLE IF NOT EXISTS products (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		product_name TEXT NOT NULL,
		tags TEXT NOT NULL
	);`
	_, err = db.Exec(createTableQuery)
	if err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}

	// Route to get products by tags
	app.Get("/recommender", func(c *fiber.Ctx) error {
		tags := c.Query("tags")
		if tags == "" {
			return c.Status(fiber.StatusBadRequest).SendString("Tags query parameter is required")
		}

		// Split tags into a slice
		tagList := strings.Split(tags, ",")
		for i := range tagList {
			tagList[i] = strings.TrimSpace(tagList[i])
		}

		// Construct SQL query with parameterized placeholders
		query := `
		SELECT product_name, tags 
		FROM products 
		WHERE ` + strings.Repeat("tags LIKE ? OR ", len(tagList)-1) + "tags LIKE ?"

		// Prepare arguments for the query
		args := make([]interface{}, len(tagList))
		for i, tag := range tagList {
			args[i] = "%" + tag + "%"
		}

		// Execute query
		rows, err := db.Query(query, args...)
		if err != nil {
			log.Printf("Failed to execute query: %v", err)
			return c.Status(fiber.StatusInternalServerError).SendString("Internal Server Error")
		}
		defer rows.Close()

		// Build HTML response
		var htmlResponse strings.Builder
		htmlResponse.WriteString("<html><body><ul>")
		for rows.Next() {
			var productName, tags string
			if err := rows.Scan(&productName, &tags); err != nil {
				log.Printf("Failed to scan row: %v", err)
				return c.Status(fiber.StatusInternalServerError).SendString("Internal Server Error")
			}
			htmlResponse.WriteString("<li>")
			htmlResponse.WriteString("Product: " + productName + " | Tags: " + tags)
			htmlResponse.WriteString("</li>")
		}
		htmlResponse.WriteString("</ul></body></html>")

		return c.Type("text/html").SendString(htmlResponse.String())
	})

	// Route to post a new product
	app.Post("/recommender", func(c *fiber.Ctx) error {
		// Parse JSON body
		var body struct {
			ProductName string   `json:"product_name"`
			Tags        []string `json:"tags"`
		}
		if err := c.BodyParser(&body); err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid input")
		}

		// Validate input
		if body.ProductName == "" || len(body.Tags) == 0 {
			return c.Status(fiber.StatusBadRequest).SendString("Product name and tags are required")
		}

		// Join tags into a single string
		tags := strings.Join(body.Tags, ",")

		// Insert product into database using parameterized query
		insertQuery := `INSERT INTO products (product_name, tags) VALUES (?, ?)`
		_, err := db.Exec(insertQuery, body.ProductName, tags)
		if err != nil {
			log.Printf("Failed to insert product: %v", err)
			return c.Status(fiber.StatusInternalServerError).SendString("Internal Server Error")
		}

		return c.SendString("Product added successfully")
	})

	// Start the server
	port := "5000"
	if os.Getenv("PORT") != "" {
		port = os.Getenv("PORT")
	}
	log.Fatal(app.Listen("0.0.0.0:" + port))
}