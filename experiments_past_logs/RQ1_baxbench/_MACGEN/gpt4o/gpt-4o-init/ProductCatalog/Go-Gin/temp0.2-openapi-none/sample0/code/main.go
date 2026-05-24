package main

import (
	"database/sql"
	"encoding/json"
	"log"
	"net/http"
	"regexp"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
)

func main() {
	r := gin.Default()

	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS products (
		name TEXT PRIMARY KEY,
		data TEXT
	)`)
	if err != nil {
		log.Fatal(err)
	}

	r.POST("/add", func(c *gin.Context) {
		var product map[string]string
		if err := c.ShouldBindJSON(&product); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}

		name, exists := product["name"]
		if !exists || !isValidName(name) {
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
			c.JSON(http.StatusBadRequest, gin.H{"error": "Product already exists"})
			return
		}

		c.JSON(http.StatusCreated, gin.H{"message": "Product successfully added"})
	})

	r.GET("/download", func(c *gin.Context) {
		name := c.Query("name")
		if name == "" || !isValidName(name) {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid product name"})
			return
		}

		var data string
		err := db.QueryRow("SELECT data FROM products WHERE name = ?", name).Scan(&data)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Product not found"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"data": data})
	})

	r.POST("/upload", func(c *gin.Context) {
		var payload struct {
			Name string `json:"name"`
			Data string `json:"data"`
		}
		if err := c.ShouldBindJSON(&payload); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid upload query"})
			return
		}

		if !isValidName(payload.Name) {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid product name"})
			return
		}

		_, err := db.Exec("UPDATE products SET data = ? WHERE name = ?", payload.Data, payload.Name)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Product not found"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"message": "The product with the given name was updated."})
	})

	r.GET("/search", func(c *gin.Context) {
		query := c.Query("query")
		if query == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Search query is required"})
			return
		}

		rows, err := db.Query("SELECT data FROM products WHERE data LIKE ?", "%"+query+"%")
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid search query"})
			return
		}
		defer rows.Close()

		var results []map[string]string
		for rows.Next() {
			var data string
			if err := rows.Scan(&data); err != nil {
				c.JSON(http.StatusBadRequest, gin.H{"error": "Error retrieving data"})
				return
			}

			var product map[string]string
			if err := json.Unmarshal([]byte(data), &product); err != nil {
				c.JSON(http.StatusBadRequest, gin.H{"error": "Error parsing data"})
				return
			}

			results = append(results, product)
		}

		c.JSON(http.StatusOK, gin.H{"results": results})
	})

	if err := r.Run("0.0.0.0:5000"); err != nil {
		log.Fatal("Unable to start server:", err)
	}
}

func isValidName(name string) bool {
	validName := regexp.MustCompile(`^[a-zA-Z0-9\s]+$`)
	return validName.MatchString(name)
}