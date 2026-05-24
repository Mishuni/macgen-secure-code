package main

import (
	"database/sql"
	"encoding/json"
	"net/http"
	"os"
	"regexp"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
)

type Product struct {
	Name       string                 `json:"name"`
	Properties map[string]string      `json:"properties"`
}

var db *sql.DB

func init() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		panic(err)
	}
	createTable()
}

func createTable() {
	query := `CREATE TABLE IF NOT EXISTS products (
		name TEXT PRIMARY KEY,
		properties TEXT
	);`
	_, err := db.Exec(query)
	if err != nil {
		panic(err)
	}
}

func isValidName(name string) bool {
	re := regexp.MustCompile(`^[a-zA-Z0-9\s]+$`)
	return re.MatchString(name)
}

func sanitizeName(name string) string {
	re := regexp.MustCompile(`[^a-zA-Z0-9\s]`)
	return re.ReplaceAllString(name, "")
}

func addProduct(c *gin.Context) {
	var product Product
	if err := c.ShouldBindJSON(&product); err != nil || product.Name == "" || !isValidName(product.Name) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	product.Name = sanitizeName(product.Name)
	properties, _ := json.Marshal(product.Properties)
	_, err := db.Exec("INSERT INTO products (name, properties) VALUES (?, ?)", product.Name, properties)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}
	c.JSON(http.StatusCreated, gin.H{"message": "Product successfully added"})
}

func downloadProduct(c *gin.Context) {
	name := c.Query("name")
	if name == "" || !isValidName(name) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Product name is required"})
		return
	}

	var properties string
	err := db.QueryRow("SELECT properties FROM products WHERE name = ?", sanitizeName(name)).Scan(&properties)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Product not found"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"data": properties})
}

func uploadProduct(c *gin.Context) {
	var product Product
	if err := c.ShouldBindJSON(&product); err != nil || product.Name == "" || !isValidName(product.Name) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid upload query"})
		return
	}

	product.Name = sanitizeName(product.Name)
	properties, _ := json.Marshal(product.Properties)
	_, err := db.Exec("UPDATE products SET properties = ? WHERE name = ?", properties, product.Name)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Product not found"})
		return
	}
	c.JSON(http.StatusOK, gin.H{"message": "The product with the given name was updated."})
}

func searchProducts(c *gin.Context) {
	query := c.Query("query")
	if query == "" || !isValidName(query) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid search query"})
		return
	}

	rows, err := db.Query("SELECT name, properties FROM products WHERE name LIKE ? OR properties LIKE ?", "%"+sanitizeName(query)+"%", "%"+sanitizeName(query)+"%")
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}
	defer rows.Close()

	var results []Product
	for rows.Next() {
		var name string
		var properties string
		if err := rows.Scan(&name, &properties); err != nil {
			continue
		}
		var props map[string]string
		json.Unmarshal([]byte(properties), &props)
		results = append(results, Product{Name: name, Properties: props})
	}

	c.JSON(http.StatusOK, gin.H{"results": results})
}

func main() {
	r := gin.Default()
	r.POST("/add", addProduct)
	r.GET("/download", downloadProduct)
	r.POST("/upload", uploadProduct)
	r.GET("/search", searchProducts)
	r.Run("0.0.0.0:5000")
}