package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"net/http"
	"regexp"
	"strconv"
	"strings"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
)

type Merchant struct {
	ID       int64  `json:"id"`
	Email    string `json:"email"`
	Name     string `json:"name"`
	Password string `json:"password"`
}

type Ware struct {
	ID          int64   `json:"id"`
	Name        string  `json:"name"`
	Description string  `json:"description"`
	Price       float64 `json:"price"`
	MerchantID  int64   `json:"merchant_id"`
}

var db *sql.DB

func main() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		panic(err)
	}
	defer db.Close()

	createTables()

	r := gin.Default()
	r.POST("/merchants/register", registerMerchant)
	r.POST("/merchants/login", loginMerchant)
	r.POST("/merchants/upload-wares", uploadWares)
	r.GET("/wares", getWares)

	r.Run("0.0.0.0:5000")
}

func createTables() {
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
		description TEXT NOT NULL,
		price REAL NOT NULL,
		merchant_id INTEGER,
		FOREIGN KEY(merchant_id) REFERENCES merchants(id)
	);`)
	if err != nil {
		panic(err)
	}
}

func isValidEmail(email string) bool {
	re := regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
	return re.MatchString(email)
}

func registerMerchant(c *gin.Context) {
	var merchant Merchant
	if err := c.ShouldBindJSON(&merchant); err != nil || !isValidEmail(merchant.Email) || len(merchant.Name) == 0 || len(merchant.Password) == 0 {
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

func loginMerchant(c *gin.Context) {
	var merchant Merchant
	if err := c.ShouldBindJSON(&merchant); err != nil || !isValidEmail(merchant.Email) || len(merchant.Password) == 0 {
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
}

func uploadWares(c *gin.Context) {
	var input struct {
		CSV string `json:"csv"`
	}
	if err := c.ShouldBindJSON(&input); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	rows := strings.Split(input.CSV, "\n")
	for _, row := range rows {
		columns := strings.Split(row, ",")
		if len(columns) != 3 {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid CSV format"})
			return
		}

		name := strings.TrimSpace(columns[0])
		description := strings.TrimSpace(columns[1])
		price := strings.TrimSpace(columns[2])

		if len(name) == 0 || len(description) == 0 || price == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid CSV format"})
			return
		}

		priceFloat, err := strconv.ParseFloat(price, 64)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid CSV format"})
			return
		}

		_, err = db.Exec("INSERT INTO wares (name, description, price) VALUES (?, ?, ?)", name, description, priceFloat)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid CSV format"})
			return
		}
	}

	c.Status(http.StatusOK)
}

func getWares(c *gin.Context) {
	minPrice := c.Query("minPrice")
	maxPrice := c.Query("maxPrice")

	query := "SELECT w.name, w.description, w.price, m.email FROM wares w JOIN merchants m ON w.merchant_id = m.id"
	var args []interface{}

	if minPrice != "" {
		query += " WHERE w.price >= ?"
		args = append(args, minPrice)
	}
	if maxPrice != "" {
		if len(args) > 0 {
			query += " AND"
		} else {
			query += " WHERE"
		}
		query += " w.price <= ?"
		args = append(args, maxPrice)
	}

	rows, err := db.Query(query, args...)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Database error"})
		return
	}
	defer rows.Close()

	var wares []Ware
	for rows.Next() {
		var ware Ware
		var merchantEmail string
		if err := rows.Scan(&ware.Name, &ware.Description, &ware.Price, &merchantEmail); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Database error"})
			return
		}
		ware.MerchantID = int64(0) // Merchant ID is not needed in the response
		wares = append(wares, ware)
	}

	c.HTML(http.StatusOK, "wares.html", gin.H{"wares": wares})
}