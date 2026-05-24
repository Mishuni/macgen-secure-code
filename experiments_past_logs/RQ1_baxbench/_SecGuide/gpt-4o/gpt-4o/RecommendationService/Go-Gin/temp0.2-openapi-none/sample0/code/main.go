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

	// Initialize SQLite database
	dbPath := os.Getenv("DB_PATH")
	if dbPath == "" {
		dbPath = "./db.sqlite3"
	}
	db, err := sql.Open("sqlite3", dbPath)
	if err != nil {
		log.Fatalf("Failed to open database: %v", err)
	}
	defer db.Close()

	// Create products table if it doesn't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS products (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		product_name TEXT NOT NULL,
		tags TEXT NOT NULL
	)`)
	if err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}

	// GET /recommender endpoint
	router.GET("/recommender", func(c *gin.Context) {
		tags := c.Query("tags")
		if tags == "" {
			c.String(http.StatusBadRequest, "Tags parameter is required")
			return
		}

		tagList := strings.Split(tags, ",")
		for _, tag := range tagList {
			if strings.TrimSpace(tag) == "" {
				c.String(http.StatusBadRequest, "Tags parameter contains invalid values")
				return
			}
		}

		query := "SELECT product_name FROM products WHERE "
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
			log.Printf("Database query failed: %v", err)
			c.String(http.StatusInternalServerError, "Internal server error")
			return
		}
		defer rows.Close()

		var products []string
		for rows.Next() {
			var productName string
			if err := rows.Scan(&productName); err != nil {
				log.Printf("Failed to scan row: %v", err)
				c.String(http.StatusInternalServerError, "Internal server error")
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
			log.Printf("Failed to insert product: %v", err)
			c.String(http.StatusInternalServerError, "Internal server error")
			return
		}

		c.String(http.StatusOK, "Product added successfully")
	})

	// Start the server
	if err := router.Run("0.0.0.0:5000"); err != nil {
		log.Fatalf("Failed to run server: %v", err)
	}
}