package main

import (
	"database/sql"
	"log"
	"net/http"
	"os"
	"strings"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
)

func main() {
	// Initialize Gin router
	router := gin.Default()

	// Initialize SQLite database
	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	// Create tables if they don't exist
	createTableQuery := `
	CREATE TABLE IF NOT EXISTS products (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		product_name TEXT NOT NULL,
		tags TEXT NOT NULL
	);`
	_, err = db.Exec(createTableQuery)
	if err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}

	// GET /recommender - Get products by tags
	router.GET("/recommender", func(c *gin.Context) {
		tags := c.Query("tags")
		if tags == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "tags query parameter is required"})
			return
		}

		// Split tags into a slice
		tagList := strings.Split(tags, ",")

		// Construct SQL query with placeholders
		query := `SELECT product_name, tags FROM products WHERE `
		conditions := make([]string, len(tagList))
		args := make([]interface{}, len(tagList))
		for i, tag := range tagList {
			conditions[i] = "tags LIKE ?"
			args[i] = "%" + strings.TrimSpace(tag) + "%"
		}
		query += strings.Join(conditions, " OR ")

		// Execute query
		rows, err := db.Query(query, args...)
		if err != nil {
			log.Printf("Failed to execute query: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
			return
		}
		defer rows.Close()

		// Collect results
		var results []string
		for rows.Next() {
			var productName, tags string
			if err := rows.Scan(&productName, &tags); err != nil {
				log.Printf("Failed to scan row: %v", err)
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
				return
			}
			results = append(results, productName+" (Tags: "+tags+")")
		}

		// Return results as HTML
		c.Data(http.StatusOK, "text/html", []byte(strings.Join(results, "<br>")))
	})

	// POST /recommender - Add a new product
	router.POST("/recommender", func(c *gin.Context) {
		var requestBody struct {
			ProductName string   `json:"product_name" binding:"required"`
			Tags        []string `json:"tags" binding:"required"`
		}

		// Bind JSON input
		if err := c.ShouldBindJSON(&requestBody); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}

		// Insert product into database
		insertQuery := `INSERT INTO products (product_name, tags) VALUES (?, ?)`
		_, err := db.Exec(insertQuery, requestBody.ProductName, strings.Join(requestBody.Tags, ","))
		if err != nil {
			log.Printf("Failed to insert product: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"message": "Product added successfully"})
	})

	// Start the server
	port := "5000"
	if os.Getenv("PORT") != "" {
		port = os.Getenv("PORT")
	}
	router.Run("0.0.0.0:" + port)
}