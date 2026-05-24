package main

import (
	"database/sql"
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
	_ "github.com/mattn/go-sqlite3"
	"golang.org/x/crypto/bcrypt"
)

var jwtKey []byte

func init() {
	jwtKey = []byte(os.Getenv("APP_SECRET"))
	if len(jwtKey) == 0 {
		log.Fatal("APP_SECRET environment variable is not set")
	}
}

func main() {
	r := gin.Default()

	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	createTable(db)

	r.POST("/login", func(c *gin.Context) {
		var creds struct {
			Email    string `json:"email" binding:"required,email"`
			Password string `json:"password" binding:"required"`
		}

		if err := c.ShouldBindJSON(&creds); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid request"})
			return
		}

		var storedPassword string
		err := db.QueryRow("SELECT password FROM users WHERE email = ?", creds.Email).Scan(&storedPassword)
		if err != nil {
			c.JSON(http.StatusUnauthorized, gin.H{"message": "Invalid email or password"})
			return
		}

		if err := bcrypt.CompareHashAndPassword([]byte(storedPassword), []byte(creds.Password)); err != nil {
			c.JSON(http.StatusUnauthorized, gin.H{"message": "Invalid email or password"})
			return
		}

		token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
			"email": creds.Email,
		})

		tokenString, err := token.SignedString(jwtKey)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"message": "Could not generate token"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"token": tokenString, "message": "Login successful"})
	})

	r.POST("/register", func(c *gin.Context) {
		var newUser struct {
			Email    string `json:"email" binding:"required,email"`
			Password string `json:"password" binding:"required"`
			Name     string `json:"name" binding:"required"`
		}

		if err := c.ShouldBindJSON(&newUser); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid request"})
			return
		}

		var exists bool
		err := db.QueryRow("SELECT EXISTS(SELECT 1 FROM users WHERE email=?)", newUser.Email).Scan(&exists)
		if err != nil || exists {
			c.JSON(http.StatusBadRequest, gin.H{"message": "Email already in use"})
			return
		}

		hashedPassword, err := bcrypt.GenerateFromPassword([]byte(newUser.Password), bcrypt.DefaultCost)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"message": "Could not register user"})
			return
		}

		_, err = db.Exec("INSERT INTO users (email, password, name) VALUES (?, ?, ?)", newUser.Email, string(hashedPassword), newUser.Name)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"message": "Could not register user"})
			return
		}

		c.JSON(http.StatusCreated, gin.H{"message": "Registration successful"})
	})

	r.Run("0.0.0.0:5000")
}

func createTable(db *sql.DB) {
	createTableSQL := `CREATE TABLE IF NOT EXISTS users (
		"id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,		
		"email" TEXT NOT NULL UNIQUE,
		"password" TEXT NOT NULL,
		"name" TEXT NOT NULL
	);`

	if _, err := db.Exec(createTableSQL); err != nil {
		log.Fatalf("Could not create table: %v", err)
	}
}