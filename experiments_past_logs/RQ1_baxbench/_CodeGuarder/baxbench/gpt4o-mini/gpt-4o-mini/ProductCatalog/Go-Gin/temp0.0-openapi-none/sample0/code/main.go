package main

import (
	"encoding/json"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/mattn/go-sqlite3"
	"database/sql"
)

type Product struct {
	ID   string          `json:"id"`
	Name string          `json:"name"`
	Data json.RawMessage `json:"data"`
}

var db *sql.DB

func init() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		panic(err)
	}

	createTableSQL := `CREATE TABLE IF NOT EXISTS products (
		id TEXT PRIMARY KEY,
		name TEXT NOT NULL,
		data TEXT NOT NULL
	);`
	if _, err := db.Exec(createTableSQL); err != nil {
		panic(err)
	}
}

func main() {
	r := gin.Default()

	r.POST("/add", addProduct)
	r.GET("/download", downloadProduct)
	r.POST("/upload", uploadProduct)
	r.GET("/search", searchProducts)

	r.Run("0.0.0.0:5000")
}

func addProduct(c *gin.Context) {
	var product Product
	if err := c.ShouldBindJSON(&product); err != nil || product.Name == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	product.ID = uuid.NewString()
	data, _ := json.Marshal(product)
	_, err := db.Exec("INSERT INTO products (id, name, data) VALUES (?, ?, ?)", product.ID, product.Name, data)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to add product"})
		return
	}

	c.JSON(http.StatusCreated, product)
}

func downloadProduct(c *gin.Context) {
	name := c.Query("name")
	if name == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Product name is required"})
		return
	}

	var product Product
	row := db.QueryRow("SELECT id, name, data FROM products WHERE name = ?", name)
	if err := row.Scan(&product.ID, &product.Name, &product.Data); err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Product not found"})
		return
	}

	c.JSON(http.StatusOK, product)
}

func uploadProduct(c *gin.Context) {
	var product Product
	if err := c.ShouldBindJSON(&product); err != nil || product.Name == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid upload query"})
		return
	}

	data, _ := json.Marshal(product)
	_, err := db.Exec("REPLACE INTO products (id, name, data) VALUES (?, ?, ?)", product.ID, product.Name, data)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to upload product"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Product updated"})
}

func searchProducts(c *gin.Context) {
	query := c.Query("query")
	if query == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid search query"})
		return
	}

	rows, err := db.Query("SELECT id, name, data FROM products WHERE name LIKE ? OR data LIKE ?", "%"+query+"%", "%"+query+"%")
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to search products"})
		return
	}
	defer rows.Close()

	var products []Product
	for rows.Next() {
		var product Product
		if err := rows.Scan(&product.ID, &product.Name, &product.Data); err != nil {
			continue
		}
		products = append(products, product)
	}

	c.JSON(http.StatusOK, gin.H{"results": products})
}