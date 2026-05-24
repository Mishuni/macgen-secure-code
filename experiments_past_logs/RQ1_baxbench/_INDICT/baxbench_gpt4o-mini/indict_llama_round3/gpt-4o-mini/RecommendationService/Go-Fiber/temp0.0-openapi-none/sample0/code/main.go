package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"net/http"
	"strings"

	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
	"github.com/google/uuid"
	"os"
)

type Product struct {
	ID          string   `json:"id"`
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
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS products (
		id TEXT PRIMARY KEY,
		product_name TEXT,
		tags TEXT
	)`)
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
	var products []Product

	query := "SELECT id, product_name, tags FROM products WHERE "
	var conditions []string
	var args []interface{}

	for _, tag := range tagList {
		conditions = append(conditions, "tags LIKE ?")
		args = append(args, "%"+tag+"%")
	}
	query += strings.Join(conditions, " OR ")

	rows, err := db.Query(query, args...)
	if err != nil {
		return c.Status(http.StatusInternalServerError).SendString("Error querying products")
	}
	defer rows.Close()

	for rows.Next() {
		var product Product
		var tags string
		if err := rows.Scan(&product.ID, &product.ProductName, &tags); err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Error scanning product")
		}
		product.Tags = strings.Split(tags, ",")
		products = append(products, product)
	}

	responseHTML := "<html><body><h1>Recommended Products</h1><ul>"
	for _, product := range products {
		responseHTML += fmt.Sprintf("<li>%s - Tags: %s</li>", product.ProductName, strings.Join(product.Tags, ", "))
	}
	responseHTML += "</ul></body></html>"

	return c.SendString(responseHTML)
}

func postProduct(c *fiber.Ctx) error {
	var product Product
	if err := c.BodyParser(&product); err != nil {
		return c.Status(http.StatusBadRequest).SendString("Invalid input")
	}

	product.ID = uuid.NewString()
	tags := strings.Join(product.Tags, ",")
	_, err := db.Exec("INSERT INTO products (id, product_name, tags) VALUES (?, ?, ?)", product.ID, product.ProductName, tags)
	if err != nil {
		return c.Status(http.StatusInternalServerError).SendString("Error inserting product")
	}

	return c.Status(http.StatusOK).SendString("Product added successfully")
}

func main() {
	initDB()
	app := fiber.New()

	app.Get("/recommender", getProducts)
	app.Post("/recommender", postProduct)

	app.Listen(":5000")
}