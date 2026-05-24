package main

import (
	"database/sql"
	"encoding/csv"
	"encoding/json"
	"net/http"
	"os"
	"strconv"
	"strings"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
)

type Merchant struct {
	Email    string `json:"email"`
	Name     string `json:"name"`
	Password string `json:"password"`
}

type WaresUpload struct {
	CSV string `json:"csv"`
}

type Ware struct {
	Name        string  `json:"name"`
	Description string  `json:"description"`
	Price       float64 `json:"price"`
	MerchantEmail string `json:"merchant_email"`
}

var db *sql.DB

func main() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		panic(err)
	}
	defer db.Close()

	// Create tables
	createTable := `
	CREATE TABLE IF NOT EXISTS merchants (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		email TEXT NOT NULL UNIQUE,
		name TEXT NOT NULL,
		password TEXT NOT NULL
	);
	CREATE TABLE IF NOT EXISTS wares (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		name TEXT NOT NULL,
		description TEXT NOT NULL,
		price REAL NOT NULL,
		merchant_email TEXT NOT NULL,
		FOREIGN KEY(merchant_email) REFERENCES merchants(email)
	);`
	_, err = db.Exec(createTable)
	if err != nil {
		panic(err)
	}

	r := gin.Default()

	r.POST("/merchants/register", registerMerchant)
	r.POST("/merchants/login", merchantLogin)
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
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	c.Status(http.StatusCreated)
}

func merchantLogin(c *gin.Context) {
	var merchant Merchant
	if err := c.ShouldBindJSON(&merchant); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	var dbMerchant Merchant
	err := db.QueryRow("SELECT email, name FROM merchants WHERE email = ? AND password = ?", merchant.Email, merchant.Password).Scan(&dbMerchant.Email, &dbMerchant.Name)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid email or password"})
		return
	}

	c.JSON(http.StatusOK, "Login successful")
}

func uploadWares(c *gin.Context) {
	var waresUpload WaresUpload
	if err := c.ShouldBindJSON(&waresUpload); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid CSV format"})
		return
	}

	// For demonstration, we will use a hardcoded merchant email.
	// In a real application, this should be retrieved from the session or context.
	merchantEmail := "merchant@example.com"

	reader := csv.NewReader(strings.NewReader(waresUpload.CSV))
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

		_, err = db.Exec("INSERT INTO wares (name, description, price, merchant_email) VALUES (?, ?, ?, ?)", record[0], record[1], price, merchantEmail)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to upload wares"})
			return
		}
	}

	c.Status(http.StatusOK)
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
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error retrieving wares"})
		return
	}
	defer rows.Close()

	var wares []Ware
	for rows.Next() {
		var ware Ware
		if err := rows.Scan(&ware.Name, &ware.Description, &ware.Price, &ware.MerchantEmail); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Error scanning wares"})
			return
		}
		wares = append(wares, ware)
	}

	c.HTML(http.StatusOK, "wares.html", gin.H{"wares": wares})
}