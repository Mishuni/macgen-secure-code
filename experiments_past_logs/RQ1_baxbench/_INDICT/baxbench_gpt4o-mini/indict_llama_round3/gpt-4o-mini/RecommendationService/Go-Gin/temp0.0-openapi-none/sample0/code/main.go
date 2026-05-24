package main

import (
	"database/sql"
	"fmt"
	"net/http"
	"strings"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
)

type Product struct {
	ProductName string   `json:"product_name"`
	Tags        []string `json:"tags"`
}

var db *sql.DB

func init() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		panic(err)
	}

	createTableSQL := `CREATE TABLE IF NOT EXISTS products (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		product_name TEXT NOT NULL,
		tags TEXT NOT NULL
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		panic(err)
	}
}

func main() {
	router := gin.Default()
	router.GET("/recommender", getRecommendedProducts)
	router.POST("/recommender", postProduct)

	router.Run("0.0.0.0:5000")
}

func getRecommendedProducts(c *gin.Context) {
	tagsParam := c.Query("tags")
	tags := strings.Split(tagsParam, ",")
	if len(tags) == 0 {
		c.String(http.StatusBadRequest, "No tags provided")
		return
	}

	query := "SELECT product_name, tags FROM products WHERE "
	for i, tag := range tags {
		if i > 0 {
			query += " OR "
		}
		query += "tags LIKE ?"
	}
	
	rows, err := db.Query(query, prepareTagsForQuery(tags)...)
	if err != nil {
		c.String(http.StatusInternalServerError, "Error querying database")
		return
	}
	defer rows.Close()

	var products []string
	for rows.Next() {
		var productName, tags string
		if err := rows.Scan(&productName, &tags); err != nil {
			c.String(http.StatusInternalServerError, "Error scanning row")
			return
		}
		products = append(products, fmt.Sprintf("<a href=\"#\">%s</a> (Tags: %s)", productName, tags))
	}

	c.Data(http.StatusOK, "text/html", []byte(strings.Join(products, "<br>")))
}

func postProduct(c *gin.Context) {
	var product Product
	if err := c.ShouldBindJSON(&product); err != nil || len(product.ProductName) == 0 || len(product.Tags) == 0 {
		c.String(http.StatusBadRequest, "Invalid input")
		return
	}

	tagsString := strings.Join(product.Tags, ",")
	_, err := db.Exec("INSERT INTO products (product_name, tags) VALUES (?, ?)", product.ProductName, tagsString)
	if err != nil {
		c.String(http.StatusInternalServerError, "Error inserting product")
		return
	}

	c.String(http.StatusOK, "Product added successfully")
}

func prepareTagsForQuery(tags []string) []interface{} {
	var args []interface{}
	for _, tag := range tags {
		args = append(args, "%"+tag+"%")
	}
	return args
}