package main

import (
	"database/sql"
	"encoding/json"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
	"github.com/mattn/go-sqlite3"
	"github.com/google/uuid"
)

type Product struct {
	Name string                 `json:"name"`
	Data map[string]interface{} `json:"data"`
}

var db *sql.DB

func main() {
	var err error
	db, err = sql.Open("sqlite3", getDatabasePath())
	if err != nil {
		handleError(err)
	}
	defer db.Close()

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS products (
		id TEXT PRIMARY KEY,
		name TEXT NOT NULL UNIQUE,
		data TEXT NOT NULL
	)`)
	if err != nil {
		handleError(err)
	}

	r := gin.Default()

	r.POST("/add", addProduct)
	r.GET("/download", downloadProduct)
	r.POST("/upload", uploadProduct)
	r.GET("/search", searchProducts)

	r.Run("0.0.0.0:5000")
}

func getDatabasePath() string {
	if path := os.Getenv("DATABASE_PATH"); path != "" {
		return path
	}
	return "./db.sqlite3"
}

func handleError(err error) {
	// Log the error and return a generic message
	// In a real application, you would log this to a file or monitoring system
	println(err.Error())
	http.Error(gin.DefaultWriter, "An error occurred", http.StatusInternalServerError)
}

func addProduct(c *gin.Context) {
	var product Product
	if err := c.ShouldBindJSON(&product); err != nil || product.Name == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	id := uuid.New().String()
	data, err := json.Marshal(product.Data)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to marshal product data"})
		return
	}

	_, err = db.Exec("INSERT INTO products (id, name, data) VALUES (?, ?, ?)", id, product.Name, data)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "An error occurred"})
		return
	}

	c.JSON(http.StatusCreated, gin.H{"message": "Product successfully added"})
}

func downloadProduct(c *gin.Context) {
	name := c.Query("name")
	if name == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Product name is required"})
		return
	}

	var data string
	err := db.QueryRow("SELECT data FROM products WHERE name = ?", name).Scan(&data)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Product not found"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"data": data})
}

func uploadProduct(c *gin.Context) {
	var product Product
	if err := c.ShouldBindJSON(&product); err != nil || product.Name == "" || product.Data == nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid upload query"})
		return
	}

	data, err := json.Marshal(product.Data)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to marshal product data"})
		return
	}

	_, err = db.Exec("REPLACE INTO products (name, data) VALUES (?, ?)", product.Name, data)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "An error occurred"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Product updated"})
}

func searchProducts(c *gin.Context) {
	query := c.Query("query")
	if query == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Search query is required"})
		return
	}

	rows, err := db.Query("SELECT name, data FROM products WHERE name LIKE ? OR data LIKE ?", "%"+query+"%", "%"+query+"%")
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to search products"})
		return
	}
	defer rows.Close()

	var results []Product
	for rows.Next() {
		var product Product
		var data string
		if err := rows.Scan(&product.Name, &data); err != nil {
			continue
		}
		if err := json.Unmarshal([]byte(data), &product.Data); err != nil {
			continue
		}
		results = append(results, product)
	}

	c.JSON(http.StatusOK, gin.H{"results": results})
}