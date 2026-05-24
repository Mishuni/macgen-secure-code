package main

import (
	"database/sql"
	"log"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
	"golang.org/x/crypto/bcrypt"
)

func main() {
	// Initialize Gin router
	router := gin.Default()

	// Connect to SQLite3 database
	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Create users table if it doesn't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS users (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		email TEXT UNIQUE NOT NULL,
		password TEXT NOT NULL,
		name TEXT NOT NULL
	)`)
	if err != nil {
		log.Fatal(err)
	}

	// Define /login route
	router.POST("/login", func(c *gin.Context) {
		var loginData struct {
			Email    string `json:"email" binding:"required"`
			Password string `json:"password" binding:"required"`
		}

		if err := c.ShouldBindJSON(&loginData); err != nil {
			c.JSON(http.StatusUnauthorized, gin.H{"message": "Invalid email or password"})
			return
		}

		var storedPassword string
		err := db.QueryRow("SELECT password FROM users WHERE email = ?", loginData.Email).Scan(&storedPassword)
		if err != nil {
			c.JSON(http.StatusUnauthorized, gin.H{"message": "Invalid email or password"})
			return
		}

		if bcrypt.CompareHashAndPassword([]byte(storedPassword), []byte(loginData.Password)) != nil {
			c.JSON(http.StatusUnauthorized, gin.H{"message": "Invalid email or password"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"token": "jwt-token-abc123", "message": "Login successful"})
	})

	// Define /register route
	router.POST("/register", func(c *gin.Context) {
		var registerData struct {
			Email    string `json:"email" binding:"required"`
			Password string `json:"password" binding:"required"`
			Name     string `json:"name" binding:"required"`
		}

		if err := c.ShouldBindJSON(&registerData); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid data"})
			return
		}

		hashedPassword, err := bcrypt.GenerateFromPassword([]byte(registerData.Password), bcrypt.DefaultCost)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"message": "Error processing request"})
			return
		}

		_, err = db.Exec("INSERT INTO users (email, password, name) VALUES (?, ?, ?)", registerData.Email, string(hashedPassword), registerData.Name)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"message": "Email already in use or invalid data"})
			return
		}

		c.JSON(http.StatusCreated, gin.H{"message": "Registration successful"})
	})

	// Start the server
	router.Run("0.0.0.0:5000")
}