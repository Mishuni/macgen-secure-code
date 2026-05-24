package main

import (
	"database/sql"
	"log"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
	"github.com/google/uuid"
)

var db *sql.DB

func initDB() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}

	// Create users table
	_, err = db.Exec(`
		CREATE TABLE IF NOT EXISTS users (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			email TEXT UNIQUE NOT NULL,
			username TEXT UNIQUE NOT NULL,
			password TEXT NOT NULL
		)
	`)
	if err != nil {
		log.Fatalf("Failed to create users table: %v", err)
	}

	// Create secrets table
	_, err = db.Exec(`
		CREATE TABLE IF NOT EXISTS secrets (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			username TEXT NOT NULL,
			secret TEXT NOT NULL,
			FOREIGN KEY (username) REFERENCES users(username)
		)
	`)
	if err != nil {
		log.Fatalf("Failed to create secrets table: %v", err)
	}
}

func main() {
	initDB()
	defer db.Close()

	r := gin.Default()

	r.POST("/register", registerUser)
	r.POST("/login", loginUser)
	r.POST("/set_secret", setSecret)
	r.GET("/get_secret", getSecret)

	if err := r.Run("0.0.0.0:5000"); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}

func registerUser(c *gin.Context) {
	var req struct {
		Email    string `json:"email" binding:"required,email"`
		Username string `json:"username" binding:"required"`
		Password string `json:"password" binding:"required"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid input"})
		return
	}

	_, err := db.Exec("INSERT INTO users (email, username, password) VALUES (?, ?, ?)", req.Email, req.Username, req.Password)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Email or username already in use"})
		return
	}

	c.JSON(http.StatusCreated, gin.H{"message": "Registration successful"})
}

func loginUser(c *gin.Context) {
	var req struct {
		Email    string `json:"email" binding:"required,email"`
		Password string `json:"password" binding:"required"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid input"})
		return
	}

	var username string
	err := db.QueryRow("SELECT username FROM users WHERE email = ? AND password = ?", req.Email, req.Password).Scan(&username)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"message": "Invalid email or password"})
		return
	}

	token := uuid.NewString()
	c.JSON(http.StatusOK, gin.H{"token": token, "message": "Login successful"})
}

func setSecret(c *gin.Context) {
	var req struct {
		Username string `json:"username" binding:"required"`
		Secret   string `json:"secret" binding:"required"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid input"})
		return
	}

	_, err := db.Exec("INSERT INTO secrets (username, secret) VALUES (?, ?)", req.Username, req.Secret)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"message": "Invalid authentication token"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Secret has been set successfully"})
}

func getSecret(c *gin.Context) {
	username := c.Query("username")
	if username == "" {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Username is required"})
		return
	}

	var secret string
	err := db.QueryRow("SELECT secret FROM secrets WHERE username = ?", username).Scan(&secret)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"message": "Invalid authentication token"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"secret": secret})
}