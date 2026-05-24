package main

import (
	"encoding/json"
	"net/http"
	"os"
	"strings"

	"github.com/gin-gonic/gin"
	"github.com/mattn/go-sqlite3"
	"database/sql"
)

type Product struct {
	ProductName string   `json:"product_name"`
	Tags        []string `json:"tags"`
}

var db *sql.DB

func main() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		panic(err)
	}
	defer db.Close()

	createTableSQL := `CREATE TABLE IF NOT EXISTS products (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		product_name TEXT NOT NULL,
		tags TEXT NOT NULL
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		panic(err)
	}

	r := gin.Default()
	r.GET("/recommender", getProducts)
	r.POST("/recommender", postProduct)
	r.Run("0.0.0.0:5000")
}

func getProducts(c *gin.Context) {
	tags := c.Query("tags")
	if tags == "" {
		c.String(http.StatusBadRequest, "Tags are required")
		return
	}

	tagList := strings.Split(tags, ",")
	query := "SELECT product_name FROM products WHERE "
	args := make([]interface{}, len(tagList))
	for i, tag := range tagList {
		if i > 0 {
			query += " OR "
		}
		query += "tags LIKE ?"
		args[i] = "%" + strings.TrimSpace(tag) + "%"
	}

	rows, err := db.Query(query, args...)
	if err != nil {
		c.String(http.StatusInternalServerError, "Database error")
		return
	}
	defer rows.Close()

	var products []string
	for rows.Next() {
		var product string
		if err := rows.Scan(&product); err != nil {
			c.String(http.StatusInternalServerError, "Error scanning product")
			return
		}
		products = append(products, product)
	}

	c.HTML(http.StatusOK, "products.html", gin.H{"products": products})
}

func postProduct(c *gin.Context) {
	var product Product
	if err := c.ShouldBindJSON(&product); err != nil || product.ProductName == "" || len(product.Tags) == 0 {
		c.String(http.StatusBadRequest, "Invalid input")
		return
	}

	_, err := db.Exec("INSERT INTO products (product_name, tags) VALUES (?, ?)", product.ProductName, strings.Join(product.Tags, ","))
	if err != nil {
		c.String(http.StatusInternalServerError, "Database error")
		return
	}
	c.String(http.StatusOK, "Product added successfully")
}