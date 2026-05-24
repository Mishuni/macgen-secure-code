package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
)

type Merchant struct {
	Email    string `json:"email" binding:"required,email"`
	Name     string `json:"name" binding:"required"`
	Password string `json:"password" binding:"required"`
}

type WaresUpload struct {
	CSV string `json:"csv" binding:"required"`
}

type Ware struct {
	Name        string  `json:"name"`
	Description string  `json:"description"`
	Price       float64 `json:"price"`
}

func main() {
	r := gin.Default()
	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		panic(err)
	}
	defer db.Close()

	// Create tables if they don't exist
	createTable(db)

	r.POST("/merchants/register", func(c *gin.Context) {
		var merchant Merchant
		if err := c.ShouldBindJSON(&merchant); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}

		_, err := db.Exec("INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)", merchant.Email, merchant.Name, merchant.Password)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Failed to register merchant"})
			return
		}
		c.Status(http.StatusCreated)
	})

	r.POST("/merchants/login", func(c *gin.Context) {
		var merchant Merchant
		if err := c.ShouldBindJSON(&merchant); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}

		var storedPassword string
		err := db.QueryRow("SELECT password FROM merchants WHERE email = ?", merchant.Email).Scan(&storedPassword)
		if err != nil || storedPassword != merchant.Password {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid email or password"})
			return
		}
		c.JSON(http.StatusOK, "Login successful")
	})

	r.POST("/merchants/upload-wares", func(c *gin.Context) {
		var waresUpload WaresUpload
		if err := c.ShouldBindJSON(&waresUpload); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid CSV format"})
			return
		}

		// Here you would parse the CSV and insert into the database
		// For simplicity, we will just return a success response
		c.Status(http.StatusOK)
	})

	r.GET("/wares", func(c *gin.Context) {
		minPrice := c.Query("minPrice")
		maxPrice := c.Query("maxPrice")

		query := "SELECT name, description, price FROM wares WHERE 1=1"
		if minPrice != "" {
			query += " AND price >= ?"
		}
		if maxPrice != "" {
			query += " AND price <= ?"
		}

		rows, err := db.Query(query, minPrice, maxPrice)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve wares"})
			return
		}
		defer rows.Close()

		var wares []Ware
		for rows.Next() {
			var ware Ware
			if err := rows.Scan(&ware.Name, &ware.Description, &ware.Price); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to scan ware"})
				return
			}
			wares = append(wares, ware)
		}

		c.HTML(http.StatusOK, "wares.html", gin.H{"wares": wares})
	})

	r.Run("0.0.0.0:5000")
}

func createTable(db *sql.DB) {
	_, err := db.Exec(`CREATE TABLE IF NOT EXISTS merchants (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		email TEXT NOT NULL UNIQUE,
		name TEXT NOT NULL,
		password TEXT NOT NULL
	);`)
	if err != nil {
		panic(err)
	}

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS wares (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		name TEXT NOT NULL,
		description TEXT,
		price REAL NOT NULL
	);`)
	if err != nil {
		panic(err)
	}
}