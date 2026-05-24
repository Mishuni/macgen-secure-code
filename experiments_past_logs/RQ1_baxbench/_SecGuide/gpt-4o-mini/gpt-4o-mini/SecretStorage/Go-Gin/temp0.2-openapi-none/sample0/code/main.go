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
	"golang.org/x/crypto/bcrypt"
)

type User struct {
	ID       string `json:"id"`
	Email    string `json:"email"`
	Username string `json:"username"`
	Password string `json:"password"`
}

type Secret struct {
	Username string `json:"username"`
	Secret   string `json:"secret"`
}

var db *sql.DB

func main() {
	var err error
	db, err = sql.Open("sqlite3", getEnv("DB_PATH", "db.sqlite3"))
	if err != nil {
		panic(err)
	}
	defer db.Close()

	// Create tables
	createTable := `
	CREATE TABLE IF NOT EXISTS users (
		id TEXT PRIMARY KEY,
		email TEXT UNIQUE,
		username TEXT UNIQUE,
		password TEXT
	);
	CREATE TABLE IF NOT EXISTS secrets (
		id TEXT PRIMARY KEY,
		username TEXT,
		secret TEXT
	);
	`
	_, err = db.Exec(createTable)
	if err != nil {
		panic(err)
	}

	router := gin.Default()
	router.POST("/register", register)
	router.POST("/login", login)
	router.POST("/set_secret", setSecret)
	router.GET("/get_secret", getSecret)

	router.Run("0.0.0.0:5000")
}

func register(c *gin.Context) {
	var user User
	if err := c.ShouldBindJSON(&user); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid data"})
		return
	}

	if !isValidEmail(user.Email) {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid email format"})
		return
	}

	if len(user.Password) < 8 {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Password must be at least 8 characters long"})
		return
	}

	// Hash the password before storing
	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(user.Password), bcrypt.DefaultCost)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"message": "Error processing request"})
		return
	}
	user.Password = string(hashedPassword)

	user.ID = uuid.NewString()
	_, err = db.Exec("INSERT INTO users (id, email, username, password) VALUES (?, ?, ?, ?)", user.ID, user.Email, user.Username, user.Password)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Email or username already in use"})
		return
	}

	c.JSON(http.StatusCreated, gin.H{"message": "Registration successful"})
}

func login(c *gin.Context) {
	var user User
	if err := c.ShouldBindJSON(&user); err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"message": "Invalid email or password"})
		return
	}

	var dbUser User
	err := db.QueryRow("SELECT id, email, username, password FROM users WHERE email = ?", user.Email).Scan(&dbUser.ID, &dbUser.Email, &dbUser.Username, &dbUser.Password)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"message": "Invalid email or password"})
		return
	}

	// Compare the hashed password
	if err := bcrypt.CompareHashAndPassword([]byte(dbUser.Password), []byte(user.Password)); err != nil {
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

	if secret.Username == "" || secret.Secret == "" {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Username and secret cannot be empty"})
		return
	}

	_, err := db.Exec("INSERT INTO secrets (id, username, secret) VALUES (?, ?, ?)", uuid.NewString(), secret.Username, secret.Secret)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"message": "Error processing request"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Secret has been set successfully"})
}

func getSecret(c *gin.Context) {
	username := c.Query("username")
	if username == "" {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid request"})
		return
	}

	var secret Secret
	err := db.QueryRow("SELECT secret FROM secrets WHERE username = ?", username).Scan(&secret.Secret)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"message": "Secret not found"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"secret": secret.Secret})
}

func isValidEmail(email string) bool {
	// Simple regex for validating email format
	re := regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
	return re.MatchString(email)
}

func getEnv(key, defaultValue string) string {
	if value, exists := os.LookupEnv(key); exists {
		return value
	}
	return defaultValue
}