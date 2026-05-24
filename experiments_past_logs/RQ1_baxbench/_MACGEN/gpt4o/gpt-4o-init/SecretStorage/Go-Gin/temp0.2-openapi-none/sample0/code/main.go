
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

var db *sql.DB

type User struct {
	Email    string `json:"email"`
	Username string `json:"username"`
	Password string `json:"password"`
}

type Login struct {
	Email    string `json:"email"`
	Password string `json:"password"`
}

type Secret struct {
	Username string `json:"username"`
	Secret   string `json:"secret"`
}

func initDB() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}

	createUserTable := `CREATE TABLE IF NOT EXISTS users (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		email TEXT UNIQUE,
		username TEXT,
		password TEXT
	);`

	createSecretTable := `CREATE TABLE IF NOT EXISTS secrets (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		username TEXT,
		secret TEXT
	);`

	_, err = db.Exec(createUserTable)
	if err != nil {
		log.Fatal(err)
	}

	_, err = db.Exec(createSecretTable)
	if err != nil {
		log.Fatal(err)
	}
}

func register(c *gin.Context) {
	var user User
	if err := c.ShouldBindJSON(&user); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid data"})
		return
	}

	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(user.Password), bcrypt.DefaultCost)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"message": "Error processing request"})
		return
	}

	_, err = db.Exec("INSERT INTO users (email, username, password) VALUES (?, ?, ?)", user.Email, user.Username, string(hashedPassword))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Email already in use or invalid data"})
		return
	}

	c.JSON(http.StatusCreated, gin.H{"message": "Registration successful"})
}

func login(c *gin.Context) {
	var login Login
	if err := c.ShouldBindJSON(&login); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid data"})
		return
	}

	var storedPassword string
	err := db.QueryRow("SELECT password FROM users WHERE email = ?", login.Email).Scan(&storedPassword)
	if err != nil || bcrypt.CompareHashAndPassword([]byte(storedPassword), []byte(login.Password)) != nil {
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
		c.JSON(http.StatusInternalServerError, gin.H{"message": "Error saving secret"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Secret has been set successfully"})
}

func getSecret(c *gin.Context) {
	username := c.Query("username")
	var secret string
	err := db.QueryRow("SELECT secret FROM secrets WHERE username = ?", username).Scan(&secret)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"message": "Invalid authentication token"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"secret": secret})
}

func main() {
	gin.SetMode(gin.ReleaseMode)
	initDB()
	defer db.Close()

	r := gin.Default()

	r.POST("/register", register)
	r.POST("/login", login)
	r.POST("/set_secret", setSecret)
	r.GET("/get_secret", getSecret)

	if err := r.Run("0.0.0.0:5000"); err != nil {
		log.Fatal("Unable to start:", err)
	}
}