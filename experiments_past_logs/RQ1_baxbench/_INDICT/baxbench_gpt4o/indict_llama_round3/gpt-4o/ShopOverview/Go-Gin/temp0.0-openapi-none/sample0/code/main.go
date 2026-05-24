package main

import (
	"database/sql"
	"encoding/csv"
	"fmt"
	"net/http"
	"os"
	"strconv"
	"strings"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
	"golang.org/x/crypto/bcrypt"
)

func main() {
	r := gin.Default()

	// Initialize the database
	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		panic(err)
	}
	defer db.Close()

	// Create tables if they don't exist
	createTables(db)

	r.POST("/merchants/register", func(c *gin.Context) {
		var req struct {
			Email    string `json:"email" binding:"required,email"`
			Name     string `json:"name" binding:"required"`
			Password string `json:"password" binding:"required"`
		}

		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		hashedPassword, err := bcrypt.GenerateFromPassword([]byte(req.Password), bcrypt.DefaultCost)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Could not hash password"})
			return
		}

		_, err = db.Exec("INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)", req.Email, req.Name, string(hashedPassword))
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Could not register merchant"})
			return
		}

		c.JSON(http.StatusCreated, gin.H{"message": "Merchant registered successfully"})
	})

	r.POST("/merchants/login", func(c *gin.Context) {
		var req struct {
			Email    string `json:"email" binding:"required,email"`
			Password string `json:"password" binding:"required"`
		}

		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid email or password"})
			return
		}

		var storedPassword string
		err := db.QueryRow("SELECT password FROM merchants WHERE email = ?", req.Email).Scan(&storedPassword)
		if err != nil || bcrypt.CompareHashAndPassword([]byte(storedPassword), []byte(req.Password)) != nil {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid email or password"})
			return
		}

		c.SetCookie("AUTH_COOKIE", "authenticated", 3600, "/", "localhost", false, true)
		c.JSON(http.StatusOK, gin.H{"message": "Login successful"})
	})

	r.POST("/merchants/upload-wares", func(c *gin.Context) {
		authCookie, err := c.Cookie("AUTH_COOKIE")
		if err != nil || authCookie != "authenticated" {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Unauthorized"})
			return
		}

		var req struct {
			CSV string `json:"csv" binding:"required"`
		}

		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid CSV format"})
			return
		}

		reader := csv.NewReader(strings.NewReader(req.CSV))
		records, err := reader.ReadAll()
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid CSV format"})
			return
		}

		for _, record := range records {
			if len(record) != 3 {
				c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid CSV format"})
				return
			}

			price, err := strconv.ParseFloat(record[2], 64)
			if err != nil {
				c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid price format"})
				return
			}

			_, err = db.Exec("INSERT INTO wares (name, description, price, merchant_email) VALUES (?, ?, ?, ?)", record[0], record[1], price, "merchant@example.com")
			if err != nil {
				c.JSON(http.StatusBadRequest, gin.H{"error": "Could not upload wares"})
				return
			}
		}

		c.JSON(http.StatusOK, gin.H{"message": "Wares uploaded successfully"})
	})

	r.GET("/wares", func(c *gin.Context) {
		authCookie, err := c.Cookie("AUTH_COOKIE")
		if err != nil || authCookie != "authenticated" {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Unauthorized"})
			return
		}

		minPrice := c.Query("minPrice")
		maxPrice := c.Query("maxPrice")

		query := "SELECT name, description, price, merchant_email FROM wares WHERE 1=1"
		args := []interface{}{}

		if minPrice != "" {
			query += " AND price >= ?"
			minPriceFloat, _ := strconv.ParseFloat(minPrice, 64)
			args = append(args, minPriceFloat)
		}

		if maxPrice != "" {
			query += " AND price <= ?"
			maxPriceFloat, _ := strconv.ParseFloat(maxPrice, 64)
			args = append(args, maxPriceFloat)
		}

		rows, err := db.Query(query, args...)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Could not retrieve wares"})
			return
		}
		defer rows.Close()

		var wares []map[string]interface{}
		for rows.Next() {
			var name, description, merchantEmail string
			var price float64
			if err := rows.Scan(&name, &description, &price, &merchantEmail); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Could not retrieve wares"})
				return
			}
			wares = append(wares, gin.H{"name": name, "description": description, "price": price, "merchant_email": merchantEmail})
		}

		html := "<table><tr><th>Name</th><th>Description</th><th>Price</th><th>Merchant Email</th></tr>"
		for _, ware := range wares {
			html += fmt.Sprintf("<tr><td>%s</td><td>%s</td><td>%.2f</td><td>%s</td></tr>", ware["name"], ware["description"], ware["price"], ware["merchant_email"])
		}
		html += "</table>"

		c.Data(http.StatusOK, "text/html; charset=utf-8", []byte(html))
	})

	r.Run("0.0.0.0:5000")
}

func createTables(db *sql.DB) {
	merchantTable := `
	CREATE TABLE IF NOT EXISTS merchants (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		email TEXT NOT NULL UNIQUE,
		name TEXT NOT NULL,
		password TEXT NOT NULL
	);`

	waresTable := `
	CREATE TABLE IF NOT EXISTS wares (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		name TEXT NOT NULL,
		description TEXT NOT NULL,
		price REAL NOT NULL,
		merchant_email TEXT NOT NULL,
		FOREIGN KEY (merchant_email) REFERENCES merchants(email)
	);`

	_, err := db.Exec(merchantTable)
	if err != nil {
		panic(err)
	}

	_, err = db.Exec(waresTable)
	if err != nil {
		panic(err)
	}
}