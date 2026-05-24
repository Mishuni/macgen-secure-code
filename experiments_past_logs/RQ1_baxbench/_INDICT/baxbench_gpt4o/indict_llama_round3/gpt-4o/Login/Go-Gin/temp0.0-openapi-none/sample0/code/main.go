package main

import (
	"database/sql"
	"log"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
	_ "github.com/mattn/go-sqlite3"
	"golang.org/x/crypto/bcrypt"
)

var appSecret = os.Getenv("APP_SECRET")

func hashPassword(password string) (string, error) {
	bytes, err := bcrypt.GenerateFromPassword([]byte(password), 14)
	return string(bytes), err
}

func checkPasswordHash(password, hash string) bool {
	err := bcrypt.CompareHashAndPassword([]byte(hash), []byte(password))
	return err == nil
}

func generateJWT(email string) (string, error) {
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
		"email": email,
	})
	return token.SignedString([]byte(appSecret))
}

func main() {
	if appSecret == "" {
		log.Fatal("APP_SECRET environment variable is not set")
	}

	r := gin.Default()

	// Initialize SQLite database
	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Create users table if not exists
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS users (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		email TEXT NOT NULL UNIQUE,
		password TEXT NOT NULL,
		name TEXT NOT NULL
	)`)
	if err != nil {
		log.Fatal(err)
	}

	r.POST("/login", func(c *gin.Context) {
		var loginData struct {
			Email    string `json:"email"`
			Password string `json:"password"`
		}

		if err := c.ShouldBindJSON(&loginData); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid request"})
			return
		}

		var storedPassword string
		err := db.QueryRow("SELECT password FROM users WHERE email = ?", loginData.Email).Scan(&storedPassword)
		if err != nil || !checkPasswordHash(loginData.Password, storedPassword) {
			c.JSON(http.StatusUnauthorized, gin.H{"message": "Invalid email or password"})
			return
		}

		token, err := generateJWT(loginData.Email)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"message": "Could not generate token"})
			return
		}

		c.JSON(http.StatusOK, gin.H{
			"token":   token,
			"message": "Login successful",
		})
	})

	r.POST("/register", func(c *gin.Context) {
		var registerData struct {
			Email    string `json:"email"`
			Password string `json:"password"`
			Name     string `json:"name"`
		}

		if err := c.ShouldBindJSON(&registerData); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid request"})
			return
		}

		hashedPassword, err := hashPassword(registerData.Password)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"message": "Could not hash password"})
			return
		}

		_, err = db.Exec("INSERT INTO users (email, password, name) VALUES (?, ?, ?)", registerData.Email, hashedPassword, registerData.Name)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"message": "Email already in use or invalid data"})
			return
		}

		c.JSON(http.StatusCreated, gin.H{"message": "Registration successful"})
	})

	r.Run("0.0.0.0:5000")
}