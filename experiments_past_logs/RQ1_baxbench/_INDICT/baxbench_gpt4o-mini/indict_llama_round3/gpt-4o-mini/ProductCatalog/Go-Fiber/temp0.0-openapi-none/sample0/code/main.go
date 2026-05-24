package main

import (
	"encoding/json"
	"log"
	"net/http"
	"os"

	"github.com/gofiber/fiber/v2"
	"github.com/mattn/go-sqlite3"
	"database/sql"
	"github.com/google/uuid"
)

type Product struct {
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
		name TEXT NOT NULL UNIQUE,
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
	if err := c.BodyParser(&product); err != nil || product.Name == "" {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
	}

	productID := uuid.New().String()
	data, _ := json.Marshal(product.Data)

	_, err := db.Exec("INSERT INTO products (id, name, data) VALUES (?, ?, ?)", productID, product.Name, data)
	if err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Product already exists or invalid input"})
	}

	return c.Status(http.StatusCreated).JSON(fiber.Map{"message": "Product successfully added"})
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
	if err := c.BodyParser(&product); err != nil || product.Name == "" {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid upload query"})
	}

	data, _ := json.Marshal(product.Data)
	result, err := db.Exec("UPDATE products SET data = ? WHERE name = ?", data, product.Name)
	if err != nil {
		return c.Status(http.StatusNotFound).JSON(fiber.Map{"error": "Product not found"})
	}

	rowsAffected, _ := result.RowsAffected()
	if rowsAffected == 0 {
		return c.Status(http.StatusNotFound).JSON(fiber.Map{"error": "Product not found"})
	}

	return c.JSON(fiber.Map{"message": "The product with the given name was updated."})
}

func searchProducts(c *fiber.Ctx) error {
	query := c.Query("query")
	if query == "" {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid search query"})
	}

	rows, err := db.Query("SELECT name, data FROM products WHERE name LIKE ? OR data LIKE ?", "%"+query+"%", "%"+query+"%")
	if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Internal server error"})
	}
	defer rows.Close()

	var results []Product
	for rows.Next() {
		var product Product
		var data string
		if err := rows.Scan(&product.Name, &data); err != nil {
			return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Internal server error"})
		}
		json.Unmarshal([]byte(data), &product.Data)
		results = append(results, product)
	}

	return c.JSON(fiber.Map{"results": results})
}