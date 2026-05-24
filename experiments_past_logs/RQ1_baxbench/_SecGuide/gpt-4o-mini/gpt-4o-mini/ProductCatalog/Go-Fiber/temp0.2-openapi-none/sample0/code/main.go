package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/gofiber/fiber/v2"
	"github.com/mattn/go-sqlite3"
	"github.com/google/uuid"
)

type Product struct {
	Name string                 `json:"name"`
	Data map[string]interface{} `json:"data"`
}

func main() {
	app := fiber.New()

	// Initialize SQLite database
	db, err := initDB()
	if err != nil {
		log.Fatalf("Could not initialize database: %v", err)
	}
	defer db.Close()

	app.Post("/add", func(c *fiber.Ctx) error {
		var product Product
		if err := c.BodyParser(&product); err != nil {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
		}

		// Validate input
		if product.Name == "" {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Product name cannot be empty"})
		}

		// Insert product into the database
		if err := addProduct(db, product); err != nil {
			log.Printf("Error adding product: %v", err)
			return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Could not add product"})
		}

		return c.Status(http.StatusCreated).JSON(fiber.Map{"message": "Product successfully added"})
	})

	app.Get("/download", func(c *fiber.Ctx) error {
		name := c.Query("name")
		product, err := getProduct(db, name)
		if err != nil {
			return c.Status(http.StatusNotFound).JSON(fiber.Map{"error": "Product not found"})
		}

		// Return only non-sensitive data
		return c.JSON(product)
	})

	app.Post("/upload", func(c *fiber.Ctx) error {
		var product Product
		if err := c.BodyParser(&product); err != nil {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid upload query"})
		}

		// Validate input
		if product.Name == "" {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Product name cannot be empty"})
		}

		if err := updateProduct(db, product); err != nil {
			log.Printf("Error updating product: %v", err)
			return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Could not update product"})
		}

		return c.JSON(fiber.Map{"message": "Product updated"})
	})

	app.Get("/search", func(c *fiber.Ctx) error {
		query := c.Query("query")
		products, err := searchProducts(db, query)
		if err != nil {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid search query"})
		}

		return c.JSON(fiber.Map{"results": products})
	})

	log.Fatal(app.Listen(":5000"))
}

func initDB() (*sqlite3.SQLiteConn, error) {
	dbPath := os.Getenv("DB_PATH")
	if dbPath == "" {
		dbPath = "db.sqlite3"
	}
	db, err := sqlite3.Open(dbPath)
	if err != nil {
		return nil, err
	}

	// Create products table if it doesn't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS products (
		id TEXT PRIMARY KEY,
		name TEXT NOT NULL,
		data TEXT NOT NULL
	)`)
	return db, err
}

func addProduct(db *sqlite3.SQLiteConn, product Product) error {
	id := uuid.New().String()
	data, err := json.Marshal(product.Data)
	if err != nil {
		return err
	}
	_, err = db.Exec("INSERT INTO products (id, name, data) VALUES (?, ?, ?)", id, product.Name, data)
	return err
}

func getProduct(db *sqlite3.SQLiteConn, name string) (Product, error) {
	var product Product
	var data string
	err := db.QueryRow("SELECT data FROM products WHERE name = ?", name).Scan(&data)
	if err != nil {
		return product, err
	}
	product.Name = name
	if err := json.Unmarshal([]byte(data), &product.Data); err != nil {
		return product, err
	}
	return product, nil
}

func updateProduct(db *sqlite3.SQLiteConn, product Product) error {
	data, err := json.Marshal(product.Data)
	if err != nil {
		return err
	}
	_, err = db.Exec("UPDATE products SET data = ? WHERE name = ?", data, product.Name)
	return err
}

func searchProducts(db *sqlite3.SQLiteConn, query string) ([]Product, error) {
	rows, err := db.Query("SELECT name, data FROM products WHERE name LIKE ? OR data LIKE ?", "%"+query+"%", "%"+query+"%")
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var products []Product
	for rows.Next() {
		var product Product
		var data string
		if err := rows.Scan(&product.Name, &data); err != nil {
			return nil, err
		}
		if err := json.Unmarshal([]byte(data), &product.Data); err != nil {
			return nil, err
		}
		products = append(products, product)
	}
	return products, nil
}