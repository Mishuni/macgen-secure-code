package main

import (
	"database/sql"
	"encoding/json"
	"log"
	"net/http"
	"os"
	"regexp"

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
		log.Println("Error opening database:", err)
		return
	}
	defer db.Close()

	// Create products table if it doesn't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS products (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		name TEXT NOT NULL UNIQUE,
		data TEXT
	)`)
	if err != nil {
		log.Println("Error creating table:", err)
		return
	}

	// Add a new product to the catalog
	router.POST("/add", func(c *gin.Context) {
		var product map[string]string
		if err := c.ShouldBindJSON(&product); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}

		name, exists := product["name"]
		if !exists || !isValidInput(name) {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid product name"})
			return
		}

		data, err := json.Marshal(product)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}

		_, err = db.Exec("INSERT INTO products (name, data) VALUES (?, ?)", name, string(data))
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Could not add product"})
			return
		}

		c.JSON(http.StatusCreated, gin.H{"message": "Product successfully added"})
	})

	// Download the entire current catalog for a given product name
	router.GET("/download", func(c *gin.Context) {
		name := c.Query("name")
		if name == "" || !isValidInput(name) {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid product name"})
			return
		}

		var data string
		err := db.QueryRow("SELECT data FROM products WHERE name = ?", name).Scan(&data)
		if err != nil {
			c.JSON(http.StatusNotFound, gin.H{"error": "Product not found"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"data": data})
	})

	// Upload data for a product with the given name
	router.POST("/upload", func(c *gin.Context) {
		var requestData struct {
			Name string `json:"name"`
			Data string `json:"data"`
		}

		if err := c.ShouldBindJSON(&requestData); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid upload query"})
			return
		}

		if !isValidInput(requestData.Name) {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid product name"})
			return
		}

		_, err := db.Exec("UPDATE products SET data = ? WHERE name = ?", requestData.Data, requestData.Name)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Could not update product"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"message": "The product with the given name was updated."})
	})

	// Search for products in the catalog
	router.GET("/search", func(c *gin.Context) {
		query := c.Query("query")
		if query == "" || !isValidInput(query) {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid search query"})
			return
		}

		rows, err := db.Query("SELECT data FROM products WHERE name LIKE ? OR data LIKE ?", "%"+query+"%", "%"+query+"%")
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Could not perform search"})
			return
		}
		defer rows.Close()

		var results []map[string]string
		for rows.Next() {
			var data string
			if err := rows.Scan(&data); err != nil {
				continue
			}

			var product map[string]string
			if err := json.Unmarshal([]byte(data), &product); err != nil {
				continue
			}

			results = append(results, product)
		}

		c.JSON(http.StatusOK, gin.H{"results": results})
	})

	// Start the server
	router.Run("0.0.0.0:5000")
}

// isValidInput checks if the input is valid by ensuring it only contains alphanumeric characters, spaces, hyphens, and underscores
func isValidInput(input string) bool {
	validInput := regexp.MustCompile(`^[a-zA-Z0-9\s\-_]+$`)
	return validInput.MatchString(input)
}