package main

import (
	"database/sql"
	"encoding/json"
	"log"
	"net/http"
	"os"

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

	// Create the products table if it doesn't exist
	_, err = db.Exec(`
		CREATE TABLE IF NOT EXISTS products (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			name TEXT NOT NULL UNIQUE,
			data TEXT NOT NULL
		)
	`)
	if err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}

	// Route to add a new product
	router.POST("/add", func(c *gin.Context) {
		var product map[string]string
		if err := c.ShouldBindJSON(&product); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}

		name, exists := product["name"]
		if !exists || name == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Product name is required"})
			return
		}

		data, err := json.Marshal(product)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to process product data"})
			return
		}

		_, err = db.Exec("INSERT INTO products (name, data) VALUES (?, ?)", name, string(data))
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Failed to add product, possibly duplicate name"})
			return
		}

		c.JSON(http.StatusCreated, gin.H{"message": "Product successfully added"})
	})

	// Route to download product data
	router.GET("/download", func(c *gin.Context) {
		name := c.Query("name")
		if name == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Product name is required"})
			return
		}

		var data string
		err := db.QueryRow("SELECT data FROM products WHERE name = ?", name).Scan(&data)
		if err == sql.ErrNoRows {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Product not found"})
			return
		} else if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve product data"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"data": data})
	})

	// Route to upload product data
	router.POST("/upload", func(c *gin.Context) {
		var payload struct {
			Name string `json:"name"`
			Data string `json:"data"`
		}
		if err := c.ShouldBindJSON(&payload); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}

		if payload.Name == "" || payload.Data == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Both name and data are required"})
			return
		}

		_, err := db.Exec("UPDATE products SET data = ? WHERE name = ?", payload.Data, payload.Name)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update product data"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"message": "Product successfully updated"})
	})

	// Route to search for products
	router.GET("/search", func(c *gin.Context) {
		query := c.Query("query")
		if query == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Search query is required"})
			return
		}

		rows, err := db.Query("SELECT data FROM products WHERE name LIKE ? OR data LIKE ?", "%"+query+"%", "%"+query+"%")
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to search for products"})
			return
		}
		defer rows.Close()

		var results []map[string]string
		for rows.Next() {
			var data string
			if err := rows.Scan(&data); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to process search results"})
				return
			}

			var product map[string]string
			if err := json.Unmarshal([]byte(data), &product); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to parse product data"})
				return
			}

			results = append(results, product)
		}

		c.JSON(http.StatusOK, gin.H{"results": results})
	})

	// Start the server
	port := "5000"
	if os.Getenv("PORT") != "" {
		port = os.Getenv("PORT")
	}
	router.Run("0.0.0.0:" + port)
}