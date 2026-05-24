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

type User struct {
	Email    string `json:"email"`
	Password string `json:"password"`
	Name     string `json:"name"`
}

type LoginResponse struct {
	Token   string `json:"token"`
	Message string `json:"message"`
}

type ErrorResponse struct {
	Message string `json:"message"`
}

var db *sql.DB

func main() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		panic(err)
	}
	defer db.Close()

	// Create users table if it doesn't exist
	createTableSQL := `CREATE TABLE IF NOT EXISTS users (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		email TEXT UNIQUE NOT NULL,
		password TEXT NOT NULL,
		name TEXT NOT NULL
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		panic(err)
	}

	router := gin.Default()
	router.POST("/login", login)
	router.POST("/register", register)
	router.Run("0.0.0.0:5000")
}

func login(c *gin.Context) {
	var user User
	if err := c.ShouldBindJSON(&user); err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{Message: "Invalid input"})
		return
	}

	if !isValidEmail(user.Email) || len(user.Password) == 0 {
		c.JSON(http.StatusUnauthorized, ErrorResponse{Message: "Invalid email or password"})
		return
	}

	var storedPassword string
	err := db.QueryRow("SELECT password FROM users WHERE email = ?", user.Email).Scan(&storedPassword)
	if err != nil || storedPassword != user.Password {
		c.JSON(http.StatusUnauthorized, ErrorResponse{Message: "Invalid email or password"})
		return
	}

	c.JSON(http.StatusOK, LoginResponse{Token: "jwt-token-abc123", Message: "Login successful"})
}

func register(c *gin.Context) {
	var user User
	if err := c.ShouldBindJSON(&user); err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{Message: "Invalid input"})
		return
	}

	if !isValidEmail(user.Email) || len(user.Password) == 0 || len(user.Name) == 0 {
		c.JSON(http.StatusBadRequest, ErrorResponse{Message: "Email already in use or invalid data"})
		return
	}

	_, err := db.Exec("INSERT INTO users (email, password, name) VALUES (?, ?, ?)", user.Email, user.Password, user.Name)
	if err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{Message: "Email already in use or invalid data"})
		return
	}

	c.JSON(http.StatusCreated, gin.H{"message": "Registration successful"})
}

func isValidEmail(email string) bool {
	re := regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
	return re.MatchString(email)
}