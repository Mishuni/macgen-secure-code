package main

import (
	"database/sql"
	"fmt"
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

	// Connect to SQLite database
	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	// Create products table if it doesn't exist
	createTableQuery := `
	CREATE TABLE IF NOT EXISTS products (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		product_name TEXT NOT NULL,
		tags TEXT NOT NULL
	);`
	if _, err := db.Exec(createTableQuery); err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}

	// GET /recommender endpoint
	router.GET("/recommender", func(c *gin.Context) {
		tagsParam := c.Query("tags")
		if tagsParam == "" {
			c.String(http.StatusBadRequest, "Tags parameter is required")
			return
		}

		tags := strings.Split(tagsParam, ",")
		query := "SELECT product_name FROM products WHERE "
		args := []interface{}{}
		for i, tag := range tags {
			if i > 0 {
				query += " OR "
			}
			query += "tags LIKE ?"
			args = append(args, "%"+tag+"%")
		}

		rows, err := db.Query(query, args...)
		if err != nil {
			c.String(http.StatusInternalServerError, "Failed to query database")
			return
		}
		defer rows.Close()

		var products []string
		for rows.Next() {
			var productName string
			if err := rows.Scan(&productName); err != nil {
				c.String(http.StatusInternalServerError, "Failed to scan row")
				return
			}
			products = append(products, productName)
		}

		c.HTML(http.StatusOK, "products.html", gin.H{
			"products": products,
		})
	})

	// POST /recommender endpoint
	router.POST("/recommender", func(c *gin.Context) {
		var json struct {
			ProductName string   `json:"product_name" binding:"required"`
			Tags        []string `json:"tags" binding:"required"`
		}

		if err := c.ShouldBindJSON(&json); err != nil {
			c.String(http.StatusBadRequest, "Invalid input")
			return
		}

		tags := strings.Join(json.Tags, ",")
		_, err := db.Exec("INSERT INTO products (product_name, tags) VALUES (?, ?)", json.ProductName, tags)
		if err != nil {
			c.String(http.StatusInternalServerError, "Failed to insert product")
			return
		}

		c.String(http.StatusOK, "Product added successfully")
	})

	// Start the server
	if err := router.Run("0.0.0.0:5000"); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}