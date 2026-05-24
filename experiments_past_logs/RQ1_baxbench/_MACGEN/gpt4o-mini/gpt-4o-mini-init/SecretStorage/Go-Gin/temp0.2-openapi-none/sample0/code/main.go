package main

import (
	"database/sql"
	"encoding/json"
	"net/http"
	"os"
	"regexp"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
	"github.com/google/uuid"
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

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS users (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		email TEXT UNIQUE,
		username TEXT UNIQUE,
		password TEXT
	);`)
	if err != nil {
		panic(err)
	}

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS secrets (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		username TEXT,
		secret TEXT
	);`)
	if err != nil {
		panic(err)
	}

	r := gin.Default()

	r.POST("/register", register)
	r.POST("/login", login)
	r.POST("/set_secret", setSecret)
	r.GET("/get_secret", getSecret)

	r.Run("0.0.0.0:5000")
}

func validateEmail(email string) bool {
	re := regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
	return re.MatchString(email)
}

func register(c *gin.Context) {
	var user User
	if err := c.ShouldBindJSON(&user); err != nil || !validateEmail(user.Email) || len(user.Username) < 3 || len(user.Password) < 6 {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid data"})
		return
	}

	_, err := db.Exec("INSERT INTO users (email, username, password) VALUES (?, ?, ?)", user.Email, user.Username, user.Password)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Email already in use or invalid data"})
		return
	}

	c.JSON(http.StatusCreated, gin.H{"message": "Registration successful"})
}

func login(c *gin.Context) {
	var user User
	if err := c.ShouldBindJSON(&user); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid data"})
		return
	}

	var dbUser User
	err := db.QueryRow("SELECT email, username, password FROM users WHERE email = ? AND password = ?", user.Email, user.Password).Scan(&dbUser.Email, &dbUser.Username, &dbUser.Password)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"message": "Invalid email or password"})
		return
	}

	token := uuid.New().String() // Dummy token for demonstration
	c.JSON(http.StatusOK, gin.H{"token": token, "message": "Login successful"})
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