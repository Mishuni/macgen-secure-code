package main

import (
    "database/sql"
    "encoding/json"
    "fmt"
    "log"
    "net/http"
    "strings"

    "github.com/gofiber/fiber/v2"
    _ "github.com/mattn/go-sqlite3"
)

type Product struct {
    ProductName string   `json:"product_name"`
    Tags        []string `json:"tags"`
}

func main() {
    app := fiber.New()

    // Initialize SQLite database
    db, err := sql.Open("sqlite3", "db.sqlite3")
    if err != nil {
        log.Fatal(err)
    }
    defer db.Close()

    // Create products table if it doesn't exist
    createTableSQL := `CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        tags TEXT NOT NULL
    );`
    if _, err := db.Exec(createTableSQL); err != nil {
        log.Fatal(err)
    }

    app.Get("/recommender", func(c *fiber.Ctx) error {
        tags := c.Query("tags")
        if tags == "" {
            return c.Status(http.StatusBadRequest).SendString("Tags are required")
        }

        tagList := strings.Split(tags, ",")
        query := "SELECT product_name, tags FROM products WHERE "
        conditions := make([]string, len(tagList))
        for i, tag := range tagList {
            conditions[i] = "tags LIKE ?"
        }
        query += strings.Join(conditions, " OR ")

        args := make([]interface{}, len(tagList))
        for i, tag := range tagList {
            args[i] = "%" + tag + "%"
        }

        rows, err := db.Query(query, args...)
        if err != nil {
            return c.Status(http.StatusInternalServerError).SendString("Error querying database")
        }
        defer rows.Close()

        var products []Product
        for rows.Next() {
            var product Product
            var tags string
            if err := rows.Scan(&product.ProductName, &tags); err != nil {
                return c.Status(http.StatusInternalServerError).SendString("Error scanning rows")
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
    })

    app.Post("/recommender", func(c *fiber.Ctx) error {
        var product Product
        if err := c.BodyParser(&product); err != nil {
            return c.Status(http.StatusBadRequest).SendString("Invalid input")
        }

        tags := strings.Join(product.Tags, ",")
        insertSQL := "INSERT INTO products (product_name, tags) VALUES (?, ?)"
        _, err := db.Exec(insertSQL, product.ProductName, tags)
        if err != nil {
            return c.Status(http.StatusInternalServerError).SendString("Error inserting product")
        }

        return c.Status(http.StatusOK).SendString("Product added successfully")
    })

    log.Fatal(app.Listen(":5000"))
}