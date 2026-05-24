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

type User struct {
	Email    string `json:"email"`
	Password string `json:"password"`
	Name     string `json:"name,omitempty"`
}

type Response struct {
	Message string `json:"message"`
	Token   string `json:"token,omitempty"`
}

func main() {
	r := gin.Default()
	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		panic(err)
	}
	defer db.Close()

	// Create users table if it doesn't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS users (
		id TEXT PRIMARY KEY,
		email TEXT UNIQUE NOT NULL,
		password TEXT NOT NULL,
		name TEXT NOT NULL
	);`)
	if err != nil {
		panic(err)
	}

	_ = os.Getenv("APP_SECRET") // Retrieve the application secret

	r.POST("/login", func(c *gin.Context) {
		var user User
		if err := c.ShouldBindJSON(&user); err != nil {
			c.JSON(http.StatusBadRequest, Response{Message: "Invalid input"})
			return
		}

		if matched, _ := regexp.MatchString(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`, user.Email); !matched {
			c.JSON(http.StatusBadRequest, Response{Message: "Invalid email format"})
			return
		}

		var storedPassword string
		err := db.QueryRow("SELECT password FROM users WHERE email = ?", user.Email).Scan(&storedPassword)
		if err != nil || storedPassword != user.Password {
			c.JSON(http.StatusUnauthorized, Response{Message: "Invalid email or password"})
			return
		}

		c.JSON(http.StatusOK, Response{Message: "Login successful", Token: "jwt-token-abc123"})
	})

	r.POST("/register", func(c *gin.Context) {
		var user User
		if err := c.ShouldBindJSON(&user); err != nil {
			c.JSON(http.StatusBadRequest, Response{Message: "Invalid input"})
			return
		}

		if matched, _ := regexp.MatchString(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`, user.Email); !matched {
			c.JSON(http.StatusBadRequest, Response{Message: "Invalid email format"})
			return
		}

		// Check for existing email
		var count int
		err := db.QueryRow("SELECT COUNT(*) FROM users WHERE email = ?", user.Email).Scan(&count)
		if err != nil {
			c.JSON(http.StatusInternalServerError, Response{Message: "Internal server error"})
			return
		}
		if count > 0 {
			c.JSON(http.StatusBadRequest, Response{Message: "Email already in use or invalid data"})
			return
		}

		// Insert new user
		_, err = db.Exec("INSERT INTO users (id, email, password, name) VALUES (?, ?, ?, ?)", uuid.New().String(), user.Email, user.Password, user.Name)
		if err != nil {
			c.JSON(http.StatusInternalServerError, Response{Message: "Internal server error"})
			return
		}

		c.JSON(http.StatusCreated, Response{Message: "Registration successful"})
	})

	r.Run("0.0.0.0:5000")
}