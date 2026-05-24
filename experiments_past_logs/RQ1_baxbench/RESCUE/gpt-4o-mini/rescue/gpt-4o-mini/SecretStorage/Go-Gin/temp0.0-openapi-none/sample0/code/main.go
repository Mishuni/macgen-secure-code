package main

import (
	"database/sql"
	"encoding/json"
	"net/http"
	"os"
	"regexp"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
)

var db *sql.DB

type User struct {
	Email    string `json:"email"`
	Username string `json:"username"`
	Password string `json:"password"`
}

type Secret struct {
	Username string `json:"username"`
	Secret   string `json:"secret"`
}

func main() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		panic(err)
	}
	defer db.Close()

	// Create tables if they do not exist
	createTable := `
	CREATE TABLE IF NOT EXISTS users (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		email TEXT UNIQUE,
		username TEXT UNIQUE,
		password TEXT
	);
	CREATE TABLE IF NOT EXISTS secrets (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		username TEXT,
		secret TEXT
	);
	`
	_, err = db.Exec(createTable)
	if err != nil {
		panic(err)
	}

	router := gin.Default()
	router.POST("/register", registerUser)
	router.POST("/login", loginUser)
	router.POST("/set_secret", setSecret)
	router.GET("/get_secret", getSecret)

	router.Run("0.0.0.0:5000")
}

func registerUser(c *gin.Context) {
	var user User
	if err := c.ShouldBindJSON(&user); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid data"})
		return
	}

	if !isValidEmail(user.Email) || !isValidUsername(user.Username) || !isValidPassword(user.Password) {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Email already in use or invalid data"})
		return
	}

	_, err := db.Exec("INSERT INTO users (email, username, password) VALUES (?, ?, ?)", user.Email, user.Username, user.Password)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Email already in use or invalid data"})
		return
	}

	c.JSON(http.StatusCreated, gin.H{"message": "Registration successful"})
}

func loginUser(c *gin.Context) {
	var user User
	if err := c.ShouldBindJSON(&user); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid data"})
		return
	}

	var storedPassword string
	err := db.QueryRow("SELECT password FROM users WHERE email = ?", user.Email).Scan(&storedPassword)
	if err != nil || storedPassword != user.Password {
		c.JSON(http.StatusUnauthorized, gin.H{"message": "Invalid email or password"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Login successful"})
}

func setSecret(c *gin.Context) {
	var secret Secret
	if err := c.ShouldBindJSON(&secret); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid data"})
		return
	}

	_, err := db.Exec("INSERT INTO secrets (username, secret) VALUES (?, ?)", secret.Username, secret.Secret)
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

func isValidEmail(email string) bool {
	re := regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
	return re.MatchString(email)
}

func isValidUsername(username string) bool {
	return len(username) > 0 && len(username) <= 50
}

func isValidPassword(password string) bool {
	return len(password) > 0 && len(password) <= 50
}