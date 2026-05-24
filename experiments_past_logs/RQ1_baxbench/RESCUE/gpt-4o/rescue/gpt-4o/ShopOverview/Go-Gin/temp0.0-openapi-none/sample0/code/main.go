package main

import (
	"database/sql"
	"encoding/csv"
	"errors"
	"fmt"
	"net/http"
	"os"
	"strconv"
	"strings"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
)

func main() {
	// Initialize Gin router
	r := gin.Default()

	// Initialize SQLite database
	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		panic(err)
	}
	defer db.Close()

	// Create necessary tables
	err = createTables(db)
	if err != nil {
		panic(err)
	}

	// Routes
	r.POST("/merchants/register", func(c *gin.Context) {
		handleMerchantRegister(c, db)
	})
	r.POST("/merchants/login", func(c *gin.Context) {
		handleMerchantLogin(c, db)
	})
	r.POST("/merchants/upload-wares", func(c *gin.Context) {
		handleUploadWares(c, db)
	})
	r.GET("/wares", func(c *gin.Context) {
		handleGetWares(c, db)
	})

	// Start server
	r.Run("0.0.0.0:5000")
}

func createTables(db *sql.DB) error {
	merchantTable := `
	CREATE TABLE IF NOT EXISTS merchants (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		email TEXT UNIQUE NOT NULL,
		name TEXT NOT NULL,
		password TEXT NOT NULL
	);`
	waresTable := `
	CREATE TABLE IF NOT EXISTS wares (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		name TEXT NOT NULL,
		description TEXT NOT NULL,
		price REAL NOT NULL,
		merchant_id INTEGER NOT NULL,
		FOREIGN KEY (merchant_id) REFERENCES merchants(id)
	);`
	_, err := db.Exec(merchantTable)
	if err != nil {
		return err
	}
	_, err = db.Exec(waresTable)
	return err
}

func handleMerchantRegister(c *gin.Context, db *sql.DB) {
	var req struct {
		Email    string `json:"email"`
		Name     string `json:"name"`
		Password string `json:"password"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	if req.Email == "" || req.Name == "" || req.Password == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "All fields are required"})
		return
	}

	_, err := db.Exec("INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)", req.Email, req.Name, req.Password)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Email already exists"})
		return
	}

	c.JSON(http.StatusCreated, gin.H{"message": "Merchant registered successfully"})
}

func handleMerchantLogin(c *gin.Context, db *sql.DB) {
	var req struct {
		Email    string `json:"email"`
		Password string `json:"password"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	var id int
	err := db.QueryRow("SELECT id FROM merchants WHERE email = ? AND password = ?", req.Email, req.Password).Scan(&id)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid email or password"})
		return
	}

	c.SetCookie("AUTH_COOKIE", fmt.Sprintf("%d", id), 3600, "/", "", false, true)
	c.JSON(http.StatusOK, gin.H{"message": "Login successful"})
}

func handleUploadWares(c *gin.Context, db *sql.DB) {
	authCookie, err := c.Cookie("AUTH_COOKIE")
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Unauthorized"})
		return
	}

	merchantID, err := strconv.Atoi(authCookie)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Unauthorized"})
		return
	}

	var req struct {
		CSV string `json:"csv"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	reader := csv.NewReader(strings.NewReader(req.CSV))
	records, err := reader.ReadAll()
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid CSV format"})
		return
	}

	tx, err := db.Begin()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}

	for _, record := range records {
		if len(record) != 3 {
			tx.Rollback()
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid CSV format"})
			return
		}

		name := record[0]
		description := record[1]
		price, err := strconv.ParseFloat(record[2], 64)
		if err != nil {
			tx.Rollback()
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid price in CSV"})
			return
		}

		_, err = tx.Exec("INSERT INTO wares (name, description, price, merchant_id) VALUES (?, ?, ?, ?)", name, description, price, merchantID)
		if err != nil {
			tx.Rollback()
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
			return
		}
	}

	err = tx.Commit()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Wares uploaded successfully"})
}

func handleGetWares(c *gin.Context, db *sql.DB) {
	minPriceStr := c.Query("minPrice")
	maxPriceStr := c.Query("maxPrice")

	var conditions []string
	var args []interface{}

	if minPriceStr != "" {
		minPrice, err := strconv.ParseFloat(minPriceStr, 64)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid minPrice"})
			return
		}
		conditions = append(conditions, "price >= ?")
		args = append(args, minPrice)
	}

	if maxPriceStr != "" {
		maxPrice, err := strconv.ParseFloat(maxPriceStr, 64)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid maxPrice"})
			return
		}
		conditions = append(conditions, "price <= ?")
		args = append(args, maxPrice)
	}

	query := "SELECT wares.name, wares.description, wares.price, merchants.email FROM wares JOIN merchants ON wares.merchant_id = merchants.id"
	if len(conditions) > 0 {
		query += " WHERE " + strings.Join(conditions, " AND ")
	}

	rows, err := db.Query(query, args...)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}
	defer rows.Close()

	var html strings.Builder
	html.WriteString("<table><tr><th>Name</th><th>Description</th><th>Price</th><th>Merchant Email</th></tr>")
	for rows.Next() {
		var name, description, email string
		var price float64
		err := rows.Scan(&name, &description, &price, &email)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
			return
		}
		html.WriteString(fmt.Sprintf("<tr><td>%s</td><td>%s</td><td>%.2f</td><td>%s</td></tr>", name, description, price, email))
	}
	html.WriteString("</table>")

	c.Data(http.StatusOK, "text/html", []byte(html.String()))
}