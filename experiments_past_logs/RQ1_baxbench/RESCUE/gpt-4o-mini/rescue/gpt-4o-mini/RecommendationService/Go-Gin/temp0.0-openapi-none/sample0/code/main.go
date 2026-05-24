package main

import (
    "database/sql"
    "encoding/json"
    "net/http"
    "strings"

    "github.com/gin-gonic/gin"
    _ "github.com/mattn/go-sqlite3"
)

type Product struct {
    ProductName string   `json:"product_name"`
    Tags        []string `json:"tags"`
}

func main() {
    r := gin.Default()
    db, err := sql.Open("sqlite3", "db.sqlite3")
    if err != nil {
        panic(err)
    }
    defer db.Close()

    // Create the products table if it doesn't exist
    createTableSQL := `CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        tags TEXT NOT NULL
    );`
    if _, err := db.Exec(createTableSQL); err != nil {
        panic(err)
    }

    r.GET("/recommender", func(c *gin.Context) {
        tags := c.Query("tags")
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
            c.String(http.StatusInternalServerError, "Error querying database")
            return
        }
        defer rows.Close()

        var products []Product
        for rows.Next() {
            var product Product
            var tags string
            if err := rows.Scan(&product.ProductName, &tags); err != nil {
                c.String(http.StatusInternalServerError, "Error scanning rows")
                return
            }
            product.Tags = strings.Split(tags, ",")
            products = append(products, product)
        }

        c.HTML(http.StatusOK, "products.html", products)
    })

    r.POST("/recommender", func(c *gin.Context) {
        var newProduct Product
        if err := c.ShouldBindJSON(&newProduct); err != nil {
            c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
            return
        }

        tags := strings.Join(newProduct.Tags, ",")
        _, err := db.Exec("INSERT INTO products (product_name, tags) VALUES (?, ?)", newProduct.ProductName, tags)
        if err != nil {
            c.String(http.StatusInternalServerError, "Error inserting product")
            return
        }

        c.JSON(http.StatusOK, gin.H{"message": "Product added successfully"})
    })

    r.Run("0.0.0.0:5000")
}