package main

import (
	"database/sql"
	"fmt"
	"log"
	"strings"

	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
)

func main() {
	app := fiber.New(fiber.Config{DisableStartupMessage: true})

	// Connect to SQLite database
	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Create tables if they don't exist
	createTables(db)

	// GET /recommender
	app.Get("/recommender", func(c *fiber.Ctx) error {
		tagsParam := c.Query("tags")
		if tagsParam == "" {
			return c.Status(fiber.StatusBadRequest).SendString("Tags parameter is required")
		}

		tags := strings.Split(tagsParam, ",")
		products, err := getProductsByTags(db, tags)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Error retrieving products")
		}

		return c.Status(fiber.StatusOK).SendString(products)
	})

	// POST /recommender
	app.Post("/recommender", func(c *fiber.Ctx) error {
		var requestBody struct {
			ProductName string   `json:"product_name"`
			Tags        []string `json:"tags"`
		}

		if err := c.BodyParser(&requestBody); err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid input")
		}

		if requestBody.ProductName == "" || len(requestBody.Tags) == 0 {
			return c.Status(fiber.StatusBadRequest).SendString("Product name and tags are required")
		}

		if err := addProduct(db, requestBody.ProductName, requestBody.Tags); err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Error adding product")
		}

		return c.Status(fiber.StatusOK).SendString("Product added successfully")
	})

	log.Fatal(app.Listen("0.0.0.0:5000"))
}

func createTables(db *sql.DB) {
	_, err := db.Exec(`
		CREATE TABLE IF NOT EXISTS products (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			name TEXT NOT NULL
		);
		CREATE TABLE IF NOT EXISTS tags (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			product_id INTEGER,
			tag TEXT NOT NULL,
			FOREIGN KEY(product_id) REFERENCES products(id)
		);
	`)
	if err != nil {
		log.Fatal(err)
	}
}

func getProductsByTags(db *sql.DB, tags []string) (string, error) {
	query := `
		SELECT DISTINCT p.name
		FROM products p
		JOIN tags t ON p.id = t.product_id
		WHERE t.tag IN (?` + strings.Repeat(",?", len(tags)-1) + `)
	`
	args := make([]interface{}, len(tags))
	for i, tag := range tags {
		args[i] = tag
	}

	rows, err := db.Query(query, args...)
	if err != nil {
		return "", err
	}
	defer rows.Close()

	var products []string
	for rows.Next() {
		var productName string
		if err := rows.Scan(&productName); err != nil {
			return "", err
		}
		products = append(products, productName)
	}

	return strings.Join(products, "<br>"), nil
}

func addProduct(db *sql.DB, productName string, tags []string) error {
	tx, err := db.Begin()
	if err != nil {
		return err
	}

	res, err := tx.Exec("INSERT INTO products (name) VALUES (?)", productName)
	if err != nil {
		tx.Rollback()
		return err
	}

	productID, err := res.LastInsertId()
	if err != nil {
		tx.Rollback()
		return err
	}

	for _, tag := range tags {
		_, err := tx.Exec("INSERT INTO tags (product_id, tag) VALUES (?, ?)", productID, tag)
		if err != nil {
			tx.Rollback()
			return err
		}
	}

	return tx.Commit()
}