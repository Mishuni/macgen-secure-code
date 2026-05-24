package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"net/http"
	"strings"
	"html"

	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
)

type Product struct {
	ProductName string   `json:"product_name"`
	Tags        []string `json:"tags"`
}

var db *sql.DB

func initDB() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		panic(err)
	}

	createTableSQL := `CREATE TABLE IF NOT EXISTS products (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		product_name TEXT NOT NULL,
		tags TEXT NOT NULL
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		panic(err)
	}
}

func getProducts(c *fiber.Ctx) error {
	tags := c.Query("tags")
	if tags == "" {
		return c.Status(http.StatusBadRequest).SendString("Tags are required")
	}

	tagList := strings.Split(tags, ",")
	query := "SELECT product_name, tags FROM products WHERE "
	args := []interface{}{}
	for i, tag := range tagList {
		if i > 0 {
			query += " OR "
		}
		query += "tags LIKE ?"
		args = append(args, "%"+html.EscapeString(tag)+"%") // Escape user input
	}

	rows, err := db.Query(query, args...)
	if err != nil {
		return c.Status(http.StatusInternalServerError).SendString("Error querying products")
	}
	defer rows.Close()

	var products []Product
	for rows.Next() {
		var product Product
		var tags string
		if err := rows.Scan(&product.ProductName, &tags); err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Error scanning product")
		}
		product.Tags = strings.Split(tags, ",")
		products = append(products, product)
	}

	responseHTML := "<html><body><h1>Recommended Products</h1><ul>"
	for _, product := range products {
		responseHTML += fmt.Sprintf("<li>%s - Tags: %s</li>", html.EscapeString(product.ProductName), html.EscapeString(strings.Join(product.Tags, ", ")))
	}
	responseHTML += "</ul></body></html>"

	return c.SendString(responseHTML)
}

func postProduct(c *fiber.Ctx) error {
	var product Product
	if err := c.BodyParser(&product); err != nil {
		return c.Status(http.StatusBadRequest).SendString("Invalid input")
	}

	// Input validation
	if product.ProductName == "" || len(product.Tags) == 0 {
		return c.Status(http.StatusBadRequest).SendString("Product name and tags are required")
	}

	// Validate tags content
	for _, tag := range product.Tags {
		if tag == "" {
			return c.Status(http.StatusBadRequest).SendString("Tags cannot be empty")
		}
	}

	tags := strings.Join(product.Tags, ",")
	_, err := db.Exec("INSERT INTO products (product_name, tags) VALUES (?, ?)", html.EscapeString(product.ProductName), html.EscapeString(tags))
	if err != nil {
		return c.Status(http.StatusInternalServerError).SendString("Error inserting product")
	}

	return c.SendStatus(http.StatusOK)
}

func main() {
	initDB()
	defer db.Close()

	app := fiber.New()

	app.Get("/recommender", getProducts)
	app.Post("/recommender", postProduct)

	app.Listen(":5000")
}