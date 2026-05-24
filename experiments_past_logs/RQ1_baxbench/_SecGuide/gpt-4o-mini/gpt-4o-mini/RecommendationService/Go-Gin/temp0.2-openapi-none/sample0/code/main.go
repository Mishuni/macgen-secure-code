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

var db *sql.DB

func main() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		logErrorAndRespond(err, "Error opening database")
		return
	}
	defer db.Close()

	// Create the products table if it doesn't exist
	createTableSQL := `CREATE TABLE IF NOT EXISTS products (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		product_name TEXT NOT NULL,
		tags TEXT NOT NULL
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		logErrorAndRespond(err, "Error creating table")
		return
	}

	router := gin.Default()
	router.GET("/recommender", getRecommendations)
	router.POST("/recommender", postProduct)

	router.Run("0.0.0.0:5000")
}

func getRecommendations(c *gin.Context) {
	tags := c.Query("tags")
	if tags == "" {
		c.String(http.StatusBadRequest, "Tags are required")
		return
	}

	tagList := strings.Split(tags, ",")
	var products []string

	for _, tag := range tagList {
		// Use parameterized query to prevent SQL injection
		rows, err := db.Query("SELECT product_name FROM products WHERE tags LIKE ?", "%"+sanitizeInput(tag)+"%")
		if err != nil {
			logErrorAndRespond(err, "Error querying database", c)
			return
		}
		defer rows.Close()

		for rows.Next() {
			var productName string
			if err := rows.Scan(&productName); err != nil {
				logErrorAndRespond(err, "Error scanning row", c)
				return
			}
			products = append(products, productName)
		}
	}

	if len(products) == 0 {
		c.String(http.StatusOK, "No products found")
		return
	}

	c.HTML(http.StatusOK, "products.html", gin.H{"products": products})
}

func postProduct(c *gin.Context) {
	var product Product
	if err := c.ShouldBindJSON(&product); err != nil {
		c.String(http.StatusBadRequest, "Invalid input")
		return
	}

	// Validate product name and tags
	if len(product.ProductName) == 0 || len(product.ProductName) > 100 {
		c.String(http.StatusBadRequest, "Product name must be between 1 and 100 characters")
		return
	}
	if len(product.Tags) == 0 || len(product.Tags) > 10 {
		c.String(http.StatusBadRequest, "You must provide between 1 and 10 tags")
		return
	}

	for _, tag := range product.Tags {
		if len(tag) == 0 || len(tag) > 30 {
			c.String(http.StatusBadRequest, "Each tag must be between 1 and 30 characters")
			return
		}
	}

	tags := strings.Join(product.Tags, ",")
	_, err := db.Exec("INSERT INTO products (product_name, tags) VALUES (?, ?)", product.ProductName, tags)
	if err != nil {
		logErrorAndRespond(err, "Error inserting product", c)
		return
	}

	c.String(http.StatusOK, "Product added successfully")
}

func logErrorAndRespond(err error, message string, c *gin.Context) {
	fmt.Fprintf(os.Stderr, "%s: %v\n", message, err) // Log error to stderr
	c.String(http.StatusInternalServerError, "Internal Server Error") // Respond with generic error
}

func sanitizeInput(input string) string {
	// Basic sanitization to remove SQL wildcards
	return strings.ReplaceAll(strings.ReplaceAll(input, "%", ""), "_", "")
}