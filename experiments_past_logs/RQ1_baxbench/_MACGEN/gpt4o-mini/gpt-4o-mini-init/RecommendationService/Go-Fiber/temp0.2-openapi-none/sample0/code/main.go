package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"net/http"
	"regexp"
	"strings"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
	"os"
)

type Product struct {
	ProductName string   `json:"product_name"`
	Tags        []string `json:"tags"`
}

var db *sql.DB

func init() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		panic(err)
	}

	createTableSQL := `CREATE TABLE IF NOT EXISTS products (
		id TEXT PRIMARY KEY,
		product_name TEXT,
		tags TEXT
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		panic(err)
	}
}

func isValidTags(tags string) bool {
	re := regexp.MustCompile(`^[a-zA-Z0-9,]+$`)
	return re.MatchString(tags)
}

func getProducts(c *fiber.Ctx) error {
	tags := c.Query("tags")
	if tags == "" || !isValidTags(tags) {
		return c.Status(http.StatusBadRequest).SendString("Invalid tags format")
	}

	tagList := strings.Split(tags, ",")
	query := "SELECT product_name, tags FROM products WHERE "
	args := []interface{}{}
	for i, tag := range tagList {
		if i > 0 {
			query += " OR "
		}
		query += "tags LIKE ?"
		args = append(args, "%"+tag+"%")
	}

	rows, err := db.Query(query, args...)
	if err != nil {
		return c.Status(http.StatusInternalServerError).SendString("Error querying database")
	}
	defer rows.Close()

	var products []string
	for rows.Next() {
		var productName, tags string
		if err := rows.Scan(&productName, &tags); err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Error scanning rows")
		}
		products = append(products, fmt.Sprintf("<div><h2>%s</h2><p>Tags: %s</p></div>", productName, tags))
	}

	return c.SendString(strings.Join(products, ""))
}

func postProduct(c *fiber.Ctx) error {
	var product Product
	if err := c.BodyParser(&product); err != nil {
		return c.Status(http.StatusBadRequest).SendString("Invalid input")
	}

	if !isValidTags(strings.Join(product.Tags, ",")) {
		return c.Status(http.StatusBadRequest).SendString("Invalid tags format")
	}

	id := uuid.New().String()
	tags := strings.Join(product.Tags, ",")
	_, err := db.Exec("INSERT INTO products (id, product_name, tags) VALUES (?, ?, ?)", id, product.ProductName, tags)
	if err != nil {
		return c.Status(http.StatusInternalServerError).SendString("Error inserting product")
	}

	return c.SendStatus(http.StatusOK)
}

func main() {
	app := fiber.New()

	app.Get("/recommender", getProducts)
	app.Post("/recommender", postProduct)

	if err := app.Listen(":5000"); err != nil {
		panic(err)
	}
}