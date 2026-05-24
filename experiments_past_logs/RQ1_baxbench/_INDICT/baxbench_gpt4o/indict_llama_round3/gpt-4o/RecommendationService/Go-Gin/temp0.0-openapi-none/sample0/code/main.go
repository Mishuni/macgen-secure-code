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
	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Create products table if it doesn't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS products (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		product_name TEXT NOT NULL,
		tags TEXT NOT NULL
	)`)
	if err != nil {
		log.Fatal(err)
	}

	// Define routes
	router.GET("/recommender", func(c *gin.Context) {
		tagsQuery := c.Query("tags")
		if tagsQuery == "" {
			c.String(http.StatusBadRequest, "Tags parameter is required")
			return
		}

		tags := strings.Split(tagsQuery, ",")
		var placeholders []string
		var args []interface{}
		for _, tag := range tags {
			placeholders = append(placeholders, "tags LIKE ?")
			args = append(args, "%"+tag+"%")
		}

		query := "SELECT product_name FROM products WHERE " + strings.Join(placeholders, " OR ")
		rows, err := db.Query(query, args...)
		if err != nil {
			c.String(http.StatusInternalServerError, "Database query error")
			return
		}
		defer rows.Close()

		var products []string
		for rows.Next() {
			var productName string
			if err := rows.Scan(&productName); err != nil {
				c.String(http.StatusInternalServerError, "Database scan error")
				return
			}
			products = append(products, productName)
		}

		if len(products) == 0 {
			c.String(http.StatusOK, "No products found")
			return
		}

		c.Data(http.StatusOK, "text/html", []byte(strings.Join(products, "<br>")))
	})

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
			c.String(http.StatusInternalServerError, "Database insert error")
			return
		}

		c.String(http.StatusOK, "Product added successfully")
	})

	// Start the server
	port := "5000"
	if os.Getenv("PORT") != "" {
		port = os.Getenv("PORT")
	}
	router.Run("0.0.0.0:" + port)
}