package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
)

type Product struct {
	Name string            `json:"name"`
	Data map[string]string `json:"data"`
}

var db *sql.DB

func initDB() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to open database: %v", err)
	}

	createTableQuery := `
	CREATE TABLE IF NOT EXISTS products (
		name TEXT PRIMARY KEY,
		data TEXT
	);`
	_, err = db.Exec(createTableQuery)
	if err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}
}

func addProduct(c *gin.Context) {
	var product Product
	if err := c.ShouldBindJSON(&product); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	dataJSON, err := json.Marshal(product.Data)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to process data"})
		return
	}

	_, err = db.Exec("INSERT INTO products (name, data) VALUES (?, ?) ON CONFLICT(name) DO UPDATE SET data=excluded.data", product.Name, string(dataJSON))
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

	row := db.QueryRow("SELECT data FROM products WHERE name = ?", name)
	var data string
	if err := row.Scan(&data); err != nil {
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

	_, err := db.Exec("INSERT INTO products (name, data) VALUES (?, ?) ON CONFLICT(name) DO UPDATE SET data=excluded.data", product.Name, product.Data)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update product"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Product successfully updated"})
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
		var name, data string
		if err := rows.Scan(&name, &data); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to read product data"})
			return
		}

		var dataMap map[string]string
		if err := json.Unmarshal([]byte(data), &dataMap); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to parse product data"})
			return
		}

		results = append(results, Product{Name: name, Data: dataMap})
	}

	c.JSON(http.StatusOK, gin.H{"results": results})
}

func main() {
	initDB()
	defer db.Close()

	r := gin.Default()

	r.POST("/add", addProduct)
	r.GET("/download", downloadProduct)
	r.POST("/upload", uploadProduct)
	r.GET("/search", searchProducts)

	port := "5000"
	if os.Getenv("PORT") != "" {
		port = os.Getenv("PORT")
	}

	if err := r.Run(fmt.Sprintf("0.0.0.0:%s", port)); err != nil {
		log.Fatalf("Failed to run server: %v", err)
	}
}