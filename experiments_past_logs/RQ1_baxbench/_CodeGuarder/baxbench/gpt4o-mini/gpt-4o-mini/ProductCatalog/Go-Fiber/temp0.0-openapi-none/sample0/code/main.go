package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	"github.com/mattn/go-sqlite3"
)

type Product struct {
	ID   string                 `json:"id"`
	Name string                 `json:"name"`
	Data map[string]interface{} `json:"data"`
}

var db *sql.DB

func init() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}

	createTableSQL := `CREATE TABLE IF NOT EXISTS products (
		id TEXT PRIMARY KEY,
		name TEXT NOT NULL,
		data TEXT NOT NULL
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		log.Fatal(err)
	}
}

func main() {
	app := fiber.New()

	app.Post("/add", addProduct)
	app.Get("/download", downloadProduct)
	app.Post("/upload", uploadProduct)
	app.Get("/search", searchProducts)

	log.Fatal(app.Listen(":5000"))
}

func addProduct(c *fiber.Ctx) error {
	var product Product
	if err := c.BodyParser(&product); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
	}

	product.ID = uuid.NewString()
	productData, _ := json.Marshal(product.Data)

	_, err := db.Exec("INSERT INTO products (id, name, data) VALUES (?, ?, ?)", product.ID, product.Name, string(productData))
	if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to add product"})
	}

	return c.Status(http.StatusCreated).JSON(product)
}

func downloadProduct(c *fiber.Ctx) error {
	name := c.Query("name")
	if name == "" {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Product name is required"})
	}

	row := db.QueryRow("SELECT data FROM products WHERE name = ?", name)
	var data string
	if err := row.Scan(&data); err != nil {
		return c.Status(http.StatusNotFound).JSON(fiber.Map{"error": "Product not found"})
	}

	return c.JSON(fiber.Map{"data": data})
}

func uploadProduct(c *fiber.Ctx) error {
	var product Product
	if err := c.BodyParser(&product); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid upload query"})
	}

	productData, _ := json.Marshal(product.Data)

	_, err := db.Exec("REPLACE INTO products (id, name, data) VALUES (?, ?, ?)", product.ID, product.Name, string(productData))
	if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to upload product"})
	}

	return c.Status(http.StatusOK).JSON(product)
}

func searchProducts(c *fiber.Ctx) error {
	query := c.Query("query")
	if query == "" {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Search query is required"})
	}

	rows, err := db.Query("SELECT name, data FROM products WHERE name LIKE ? OR data LIKE ?", "%"+query+"%", "%"+query+"%")
	if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to search products"})
	}
	defer rows.Close()

	var results []Product
	for rows.Next() {
		var product Product
		var data string
		if err := rows.Scan(&product.Name, &data); err != nil {
			return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to read product"})
		}
		product.Data = make(map[string]interface{})
		json.Unmarshal([]byte(data), &product.Data)
		results = append(results, product)
	}

	return c.JSON(fiber.Map{"results": results})
}