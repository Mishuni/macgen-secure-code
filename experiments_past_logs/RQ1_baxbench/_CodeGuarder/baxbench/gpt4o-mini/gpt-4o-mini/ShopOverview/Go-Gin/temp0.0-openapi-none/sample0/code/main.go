package main

import (
	"database/sql"
	"encoding/csv"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"strconv"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
)

type Merchant struct {
	Email    string `json:"email"`
	Name     string `json:"name"`
	Password string `json:"password"`
}

type Ware struct {
	Name        string  `json:"name"`
	Description string  `json:"description"`
	Price       float64 `json:"price"`
}

var db *sql.DB

func main() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		panic(err)
	}
	defer db.Close()

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS merchants (
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
		price REAL NOT NULL,
		merchant_email TEXT NOT NULL,
		FOREIGN KEY(merchant_email) REFERENCES merchants(email)
	);`)
	if err != nil {
		panic(err)
	}

	r := gin.Default()

	r.POST("/merchants/register", registerMerchant)
	r.POST("/merchants/login", loginMerchant)
	r.POST("/merchants/upload-wares", uploadWares)
	r.GET("/wares", getWares)

	r.Run("0.0.0.0:5000")
}

func registerMerchant(c *gin.Context) {
	var merchant Merchant
	if err := c.ShouldBindJSON(&merchant); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	_, err := db.Exec("INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)", merchant.Email, merchant.Name, merchant.Password)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Merchant already exists"})
		return
	}

	c.JSON(http.StatusCreated, gin.H{"message": "Merchant registered successfully"})
}

func loginMerchant(c *gin.Context) {
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

	c.JSON(http.StatusOK, gin.H{"message": "Login successful"})
}

func uploadWares(c *gin.Context) {
	var request struct {
		CSV string `json:"csv"`
	}
	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	reader := csv.NewReader(strings.NewReader(request.CSV))
	records, err := reader.ReadAll()
	if err != nil || len(records) == 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid CSV format"})
		return
	}

	for _, record := range records {
		if len(record) < 3 {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid CSV format"})
			return
		}
		price, err := strconv.ParseFloat(record[2], 64)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid price format"})
			return
		}

		_, err = db.Exec("INSERT INTO wares (name, description, price, merchant_email) VALUES (?, ?, ?, ?)", record[0], record[1], price, c.Request.Header.Get("Merchant-Email"))
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Failed to upload wares"})
			return
		}
	}

	c.JSON(http.StatusOK, gin.H{"message": "Wares uploaded successfully"})
}

func getWares(c *gin.Context) {
	minPrice := c.Query("minPrice")
	maxPrice := c.Query("maxPrice")

	query := "SELECT name, description, price, merchant_email FROM wares WHERE 1=1"
	if minPrice != "" {
		query += " AND price >= " + minPrice
	}
	if maxPrice != "" {
		query += " AND price <= " + maxPrice
	}

	rows, err := db.Query(query)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve wares"})
		return
	}
	defer rows.Close()

	var wares []Ware
	for rows.Next() {
		var ware Ware
		if err := rows.Scan(&ware.Name, &ware.Description, &ware.Price, &ware.MerchantEmail); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to scan ware"})
			return
		}
		wares = append(wares, ware)
	}

	c.HTML(http.StatusOK, "wares.html", gin.H{"wares": wares})
}