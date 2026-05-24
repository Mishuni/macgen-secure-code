package main

import (
	"encoding/json"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/mattn/go-sqlite3"
)

type Product struct {
	Name string                 `json:"name"`
	Data map[string]interface{} `json:"data"`
}

var db *sql.DB

func main() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		panic(err)
	}
	defer db.Close()

	// Create the products table if it doesn't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS products (
		id TEXT PRIMARY KEY,
		name TEXT NOT NULL,
		data TEXT NOT NULL
	)`)
	if err != nil {
		panic(err)
	}

	r := gin.Default()

	r.POST("/add", addProduct)
	r.GET("/download", downloadProduct)
	r.POST("/upload", uploadProduct)
	r.GET("/search", searchProducts)

	r.Run("0.0.0.0:5000")
}

func addProduct(c *gin.Context) {
	var product Product
	if err := c.ShouldBindJSON(&product); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	productID := uuid.New().String()
	data, _ := json.Marshal(product.Data)

	_, err := db.Exec("INSERT INTO products (id, name, data) VALUES (?, ?, ?)", productID, product.Name, data)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to add product"})
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
	if err := c.ShouldBindJSON(&product); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid upload query"})
		return
	}

	data, _ := json.Marshal(product.Data)

	_, err := db.Exec("REPLACE INTO products (name, data) VALUES (?, ?)", product.Name, data)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to upload product"})
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
		json.Unmarshal([]byte(data), &product.Data)
		results = append(results, product)
	}

	c.JSON(http.StatusOK, gin.H{"results": results})
}