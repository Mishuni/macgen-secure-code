package main

import (
	"database/sql"
	"fmt"
	"log"
	"net/http"
	"os"
	"strconv"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
	"golang.org/x/crypto/bcrypt"
)

func main() {
	r := gin.Default()

	// Initialize the database
	db, err := initDB("db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to initialize database: %v", err)
	}
	defer db.Close()

	// Set up routes
	r.POST("/merchants/register", func(c *gin.Context) {
		registerMerchant(c, db)
	})
	r.POST("/merchants/login", func(c *gin.Context) {
		loginMerchant(c, db)
	})
	r.POST("/merchants/upload-wares", func(c *gin.Context) {
		uploadWares(c, db)
	})
	r.GET("/wares", func(c *gin.Context) {
		retrieveWares(c, db)
	})

	// Start the server
	if err := r.Run("0.0.0.0:5000"); err != nil {
		log.Fatalf("Failed to run server: %v", err)
	}
}

func initDB(filepath string) (*sql.DB, error) {
	db, err := sql.Open("sqlite3", filepath)
	if err != nil {
		return nil, err
	}

	// Create tables if they don't exist
	createMerchantTable := `CREATE TABLE IF NOT EXISTS merchants (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		email TEXT UNIQUE NOT NULL,
		name TEXT NOT NULL,
		password TEXT NOT NULL
	);`
	_, err = db.Exec(createMerchantTable)
	if err != nil {
		return nil, err
	}

	createWaresTable := `CREATE TABLE IF NOT EXISTS wares (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		name TEXT NOT NULL,
		description TEXT NOT NULL,
		price REAL NOT NULL,
		merchant_id INTEGER,
		FOREIGN KEY (merchant_id) REFERENCES merchants(id)
	);`
	_, err = db.Exec(createWaresTable)
	if err != nil {
		return nil, err
	}

	return db, nil
}

func registerMerchant(c *gin.Context, db *sql.DB) {
	var req struct {
		Email    string `json:"email" binding:"required,email"`
		Name     string `json:"name" binding:"required"`
		Password string `json:"password" binding:"required"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(req.Password), bcrypt.DefaultCost)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to hash password"})
		return
	}

	_, err = db.Exec("INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)", req.Email, req.Name, string(hashedPassword))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Failed to register merchant"})
		return
	}

	c.JSON(http.StatusCreated, gin.H{"message": "Merchant registered successfully"})
}

func loginMerchant(c *gin.Context, db *sql.DB) {
	var req struct {
		Email    string `json:"email" binding:"required,email"`
		Password string `json:"password" binding:"required"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	var storedPassword string
	err := db.QueryRow("SELECT password FROM merchants WHERE email = ?", req.Email).Scan(&storedPassword)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid email or password"})
		return
	}

	if err := bcrypt.CompareHashAndPassword([]byte(storedPassword), []byte(req.Password)); err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid email or password"})
		return
	}

	c.SetCookie("AUTH_COOKIE", "authenticated", 3600, "/", "localhost", false, true)
	c.JSON(http.StatusOK, gin.H{"message": "Login successful"})
}

func uploadWares(c *gin.Context, db *sql.DB) {
	authCookie, err := c.Cookie("AUTH_COOKIE")
	if err != nil || authCookie != "authenticated" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Unauthorized"})
		return
	}

	var req struct {
		CSV string `json:"csv" binding:"required"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	// Parse CSV and insert into database
	// This is a simplified example, real CSV parsing should be more robust
	rows := strings.Split(req.CSV, "\n")
	for _, row := range rows {
		cols := strings.Split(row, ",")
		if len(cols) != 3 {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid CSV format"})
			return
		}

		name := cols[0]
		description := cols[1]
		price, err := strconv.ParseFloat(cols[2], 64)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid price format"})
			return
		}

		_, err = db.Exec("INSERT INTO wares (name, description, price) VALUES (?, ?, ?)", name, description, price)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to upload wares"})
			return
		}
	}

	c.JSON(http.StatusOK, gin.H{"message": "Wares uploaded successfully"})
}

func retrieveWares(c *gin.Context, db *sql.DB) {
	authCookie, err := c.Cookie("AUTH_COOKIE")
	if err != nil || authCookie != "authenticated" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Unauthorized"})
		return
	}

	minPriceStr := c.Query("minPrice")
	maxPriceStr := c.Query("maxPrice")

	var minPrice, maxPrice float64
	var errMin, errMax error

	if minPriceStr != "" {
		minPrice, errMin = strconv.ParseFloat(minPriceStr, 64)
		if errMin != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid minPrice"})
			return
		}
	}

	if maxPriceStr != "" {
		maxPrice, errMax = strconv.ParseFloat(maxPriceStr, 64)
		if errMax != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid maxPrice"})
			return
		}
	}

	query := "SELECT wares.name, wares.description, wares.price, merchants.email FROM wares JOIN merchants ON wares.merchant_id = merchants.id WHERE 1=1"
	args := []interface{}{}

	if minPriceStr != "" {
		query += " AND wares.price >= ?"
		args = append(args, minPrice)
	}

	if maxPriceStr != "" {
		query += " AND wares.price <= ?"
		args = append(args, maxPrice)
	}

	rows, err := db.Query(query, args...)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve wares"})
		return
	}
	defer rows.Close()

	var wares []map[string]interface{}
	for rows.Next() {
		var name, description, email string
		var price float64
		if err := rows.Scan(&name, &description, &price, &email); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to parse wares"})
			return
		}
		wares = append(wares, map[string]interface{}{
			"name":        name,
			"description": description,
			"price":       price,
			"email":       email,
		})
	}

	c.HTML(http.StatusOK, "wares.html", gin.H{"wares": wares})
}