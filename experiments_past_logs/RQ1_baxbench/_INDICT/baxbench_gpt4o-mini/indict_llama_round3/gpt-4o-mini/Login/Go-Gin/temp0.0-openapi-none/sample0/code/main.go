package main

import (
	"encoding/json"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

type User struct {
	ID       uuid.UUID `gorm:"primaryKey"`
	Email    string    `gorm:"unique"`
	Password string
	Name     string
}

var db *gorm.DB

func init() {
	var err error
	db, err = gorm.Open(sqlite.Open("db.sqlite3"), &gorm.Config{})
	if err != nil {
		panic("failed to connect database")
	}
	db.AutoMigrate(&User{})
}

func main() {
	r := gin.Default()

	r.POST("/login", login)
	r.POST("/register", register)

	r.Run("0.0.0.0:5000")
}

func login(c *gin.Context) {
	var input User
	if err := c.ShouldBindJSON(&input); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid input"})
		return
	}

	var user User
	if err := db.Where("email = ?", input.Email).First(&user).Error; err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"message": "Invalid email or password"})
		return
	}

	if user.Password != input.Password {
		c.JSON(http.StatusUnauthorized, gin.H{"message": "Invalid email or password"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"token": "jwt-token-abc123", "message": "Login successful"})
}

func register(c *gin.Context) {
	var input User
	if err := c.ShouldBindJSON(&input); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid input"})
		return
	}

	if input.Email == "" || input.Password == "" || input.Name == "" {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Email, password, and name are required"})
		return
	}

	user := User{ID: uuid.New(), Email: input.Email, Password: input.Password, Name: input.Name}

	if err := db.Create(&user).Error; err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Email already in use or invalid data"})
		return
	}

	c.JSON(http.StatusCreated, gin.H{"message": "Registration successful"})
}