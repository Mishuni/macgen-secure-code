
package main

import (
	"database/sql"
	"fmt"
	"log"
	"net/http"
	"strings"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
)

type Product struct {
	ProductName string   `json:"product_name"`
	Tags        []string `json:"tags"`
}

func main() {
	// Initialize Gin router
	router := gin.New()

	// Connect to SQLite database
	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Create tables if they don't exist
	createTables(db)

	// Define routes
	router.GET("/recommender", func(c *gin.Context) {
		tags := c.Query("tags")
		if tags == "" {
			c.String(http.StatusBadRequest, "Tags parameter is required")
			return
		}
		tagList := strings.Split(tags, ",")
		products, err := getProductsByTags(db, tagList)
		if err != nil {
			c.String(http.StatusInternalServerError, "Error retrieving products")
			return
		}
		c.Data(http.StatusOK, "text/html", []byte(products))
	})

	router.POST("/recommender", func(c *gin.Context) {
		var product Product
		if err := c.ShouldBindJSON(&product); err != nil {
			c.String(http.StatusBadRequest, "Invalid input")
			return
		}
		if err := addProduct(db, product); err != nil {
			c.String(http.StatusInternalServerError, "Error adding product")
			return
		}
		c.String(http.StatusOK, "Product added successfully")
	})

	// Start the server
	router.Run("0.0.0.0:5000")
}

func createTables(db *sql.DB) {
	createProductTable := `
	CREATE TABLE IF NOT EXISTS products (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		product_name TEXT NOT NULL
	);`
	createTagTable := `
	CREATE TABLE IF NOT EXISTS tags (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		product_id INTEGER,
		tag TEXT,
		FOREIGN KEY(product_id) REFERENCES products(id)
	);`
	_, err := db.Exec(createProductTable)
	if err != nil {
		log.Fatal(err)
	}
	_, err = db.Exec(createTagTable)
	if err != nil {
		log.Fatal(err)
	}
}

func addProduct(db *sql.DB, product Product) error {
	tx, err := db.Begin()
	if err != nil {
		return err
	}
	defer tx.Rollback()

	result, err := tx.Exec("INSERT INTO products (product_name) VALUES (?)", product.ProductName)
	if err != nil {
		return err
	}

	productID, err := result.LastInsertId()
	if err != nil {
		return err
	}

	for _, tag := range product.Tags {
		_, err := tx.Exec("INSERT INTO tags (product_id, tag) VALUES (?, ?)", productID, tag)
		if err != nil {
			return err
		}
	}

	return tx.Commit()
}

func getProductsByTags(db *sql.DB, tags []string) (string, error) {
	query := `
	SELECT DISTINCT p.product_name
	FROM products p
	JOIN tags t ON p.id = t.product_id
	WHERE t.tag IN (?` + strings.Repeat(",?", len(tags)-1) + `)`
	args := make([]interface{}, len(tags))
	for i, tag := range tags {
		args[i] = tag
	}

	rows, err := db.Query(query, args...)
	if err != nil {
		return "", err
	}
	defer rows.Close()

	var products []string
	for rows.Next() {
		var productName string
		if err := rows.Scan(&productName); err != nil {
			return "", err
		}
		products = append(products, fmt.Sprintf("<li>%s</li>", productName))
	}

	if err := rows.Err(); err != nil {
		return "", err
	}

	return "<ul>" + strings.Join(products, "") + "</ul>", nil
}