package main

import (
	"database/sql"
	"encoding/csv"
	"encoding/json"
	"net/http"
	"os"
	"strconv"
	"strings"
	"unicode"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
	"golang.org/x/crypto/bcrypt"
)

var db *sql.DB

type Merchant struct {
	Email    string `json:"email"`
	Name     string `json:"name"`
	Password string `json:"password"`
}

type Wares struct {
	Csv string `json:"csv"`
}

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

	if !isValidPassword(merchant.Password) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Password does not meet complexity requirements"})
		return
	}

	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(merchant.Password), bcrypt.DefaultCost)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}

	_, err = db.Exec("INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)", merchant.Email, merchant.Name, hashedPassword)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Email already exists"})
		return
	}

	c.Status(http.StatusCreated)
}

func loginMerchant(c *gin.Context) {
	var merchant Merchant
	if err := c.ShouldBindJSON(&merchant); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	var storedPassword string
	err := db.QueryRow("SELECT password FROM merchants WHERE email = ?", merchant.Email).Scan(&storedPassword)
	if err != nil || bcrypt.CompareHashAndPassword([]byte(storedPassword), []byte(merchant.Password)) != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid email or password"})
		return
	}

	c.JSON(http.StatusOK, "Login successful")
}

func uploadWares(c *gin.Context) {
	var wares Wares
	if err := c.ShouldBindJSON(&wares); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid CSV format"})
		return
	}

	// Here you would typically get the merchant's email from the authenticated session
	merchantEmail := "merchant@example.com" // Replace with actual merchant email

	reader := csv.NewReader(strings.NewReader(wares.Csv))
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
		name, description, priceStr := record[0], record[1], record[2]
		price, err := strconv.ParseFloat(priceStr, 64)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid CSV format"})
			return
		}

		_, err = db.Exec("INSERT INTO wares (name, description, price, merchant_email) VALUES (?, ?, ?, ?)", name, description, price, merchantEmail)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Failed to upload wares"})
			return
		}
	}

	c.Status(http.StatusOK)
}

func getWares(c *gin.Context) {
	minPrice := c.Query("minPrice")
	maxPrice := c.Query("maxPrice")

	query := "SELECT name, description, price FROM wares WHERE 1=1"
	var args []interface{}
	if minPrice != "" {
		query += " AND price >= ?"
		args = append(args, minPrice)
	}
	if maxPrice != "" {
		query += " AND price <= ?"
		args = append(args, maxPrice)
	}

	rows, err := db.Query(query, args...)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}
	defer rows.Close()

	var wares []struct {
		Name        string
		Description string
		Price       float64
	}

	for rows.Next() {
		var ware struct {
			Name        string
			Description string
			Price       float64
		}
		if err := rows.Scan(&ware.Name, &ware.Description, &ware.Price); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
			return
		}
		wares = append(wares, ware)
	}

	c.JSON(http.StatusOK, wares)
}

func isValidPassword(password string) bool {
	if len(password) < 8 {
		return false
	}
	hasUpper := false
	hasLower := false
	hasNumber := false
	for _, char := range password {
		switch {
		case unicode.IsUpper(char):
			hasUpper = true
		case unicode.IsLower(char):
			hasLower = true
		case unicode.IsDigit(char):
			hasNumber = true
		}
	}
	return hasUpper && hasLower && hasNumber
}