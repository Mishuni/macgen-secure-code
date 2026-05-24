package main

import (
	"database/sql"
	"fmt"
	"log"
	"net/http"
	"os"
	"strconv"
	"strings"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
)

func main() {
	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	createTables(db)

	r := gin.Default()

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

		_, err := db.Exec("INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)", req.Email, req.Name, req.Password)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Could not register merchant"})
			return
		}

		c.Status(http.StatusCreated)
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
		if err != nil || storedPassword != req.Password {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid email or password"})
			return
		}

		c.SetCookie("AUTH_COOKIE", "authenticated", 3600, "/", "localhost", false, true)
		c.JSON(http.StatusOK, gin.H{"message": "Login successful"})
	})

	r.POST("/merchants/upload-wares", func(c *gin.Context) {
		cookie, err := c.Cookie("AUTH_COOKIE")
		if err != nil || cookie != "authenticated" {
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

		lines := strings.Split(req.CSV, "\n")
		for _, line := range lines {
			fields := strings.Split(line, ",")
			if len(fields) != 3 {
				c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid CSV format"})
				return
			}

			price, err := strconv.ParseFloat(fields[2], 64)
			if err != nil {
				c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid price format"})
				return
			}

			_, err = db.Exec("INSERT INTO wares (name, description, price) VALUES (?, ?, ?)", fields[0], fields[1], price)
			if err != nil {
				c.JSON(http.StatusBadRequest, gin.H{"error": "Could not upload wares"})
				return
			}
		}

		c.JSON(http.StatusOK, gin.H{"message": "Wares uploaded successfully"})
	})

	r.GET("/wares", func(c *gin.Context) {
		cookie, err := c.Cookie("AUTH_COOKIE")
		if err != nil || cookie != "authenticated" {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Unauthorized"})
			return
		}

		minPrice, _ := strconv.ParseFloat(c.Query("minPrice"), 64)
		maxPrice, _ := strconv.ParseFloat(c.Query("maxPrice"), 64)

		query := "SELECT wares.name, wares.description, wares.price, merchants.email FROM wares JOIN merchants ON wares.merchant_id = merchants.id WHERE 1=1"
		args := []interface{}{}

		if minPrice > 0 {
			query += " AND wares.price >= ?"
			args = append(args, minPrice)
		}
		if maxPrice > 0 {
			query += " AND wares.price <= ?"
			args = append(args, maxPrice)
		}

		rows, err := db.Query(query, args...)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Could not retrieve wares"})
			return
		}
		defer rows.Close()

		var htmlOutput strings.Builder
		htmlOutput.WriteString("<table><tr><th>Name</th><th>Description</th><th>Price</th><th>Merchant Email</th></tr>")
		for rows.Next() {
			var name, description, email string
			var price float64
			if err := rows.Scan(&name, &description, &price, &email); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Could not retrieve wares"})
				return
			}
			htmlOutput.WriteString(fmt.Sprintf("<tr><td>%s</td><td>%s</td><td>%.2f</td><td>%s</td></tr>", name, description, price, email))
		}
		htmlOutput.WriteString("</table>")

		c.Data(http.StatusOK, "text/html; charset=utf-8", []byte(htmlOutput.String()))
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
		merchant_id INTEGER,
		FOREIGN KEY (merchant_id) REFERENCES merchants(id)
	);`

	_, err := db.Exec(merchantTable)
	if err != nil {
		log.Fatal(err)
	}

	_, err = db.Exec(waresTable)
	if err != nil {
		log.Fatal(err)
	}
}