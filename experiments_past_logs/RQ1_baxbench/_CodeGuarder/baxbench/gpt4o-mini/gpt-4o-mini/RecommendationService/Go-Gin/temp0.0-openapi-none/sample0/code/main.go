package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"strings"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
)

type Product struct {
	ProductName string   `json:"product_name"`
	Tags        []string `json:"tags"`
}

func main() {
	// Initialize the Gin router
	router := gin.Default()

	// Set up the SQLite database
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

	// GET endpoint for product recommendations
	router.GET("/recommender", func(c *gin.Context) {
		tagsQuery := c.Query("tags")
		if tagsQuery == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Tags are required"})
			return
		}

		tags := strings.Split(tagsQuery, ",")
		var products []Product

		// Query the database for products matching the tags
		rows, err := db.Query("SELECT product_name, tags FROM products WHERE tags LIKE ?", "%"+tags[0]+"%")
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Database query error"})
			return
		}
		defer rows.Close()

		for rows.Next() {
			var product Product
			var tagsString string
			if err := rows.Scan(&product.ProductName, &tagsString); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Error scanning row"})
				return
			}
			product.Tags = strings.Split(tagsString, ",")
			products = append(products, product)
		}

		c.HTML(http.StatusOK, "products.html", products)
	})

	// POST endpoint to add new products
	router.POST("/recommender", func(c *gin.Context) {
		var newProduct Product
		if err := c.ShouldBindJSON(&newProduct); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}

		// Insert the new product into the database
		tagsString := strings.Join(newProduct.Tags, ",")
		_, err := db.Exec("INSERT INTO products (product_name, tags) VALUES (?, ?)", newProduct.ProductName, tagsString)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to add product"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"message": "Product added successfully"})
	})

	// Start the web server
	router.Run("0.0.0.0:5000")
}