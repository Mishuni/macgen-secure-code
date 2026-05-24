package main

import (
	"database/sql"
	"encoding/json"
	"net/http"
	"os"
	"regexp"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
	"golang.org/x/crypto/bcrypt"
)

type Invitation struct {
	InviteID string `json:"invite_id"`
	Email    string `json:"email"`
}

type User struct {
	Username string `json:"user_name"`
	Password string `json:"password"`
	InviteID string `json:"invite_id"`
}

var db *sql.DB

func main() {
	var err error
	db, err = sql.Open("sqlite3", getDatabasePath())
	if err != nil {
		panic(err)
	}
	defer db.Close()

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS invitations (invite_id TEXT PRIMARY KEY, email TEXT UNIQUE)`)
	if err != nil {
		panic(err)
	}

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)`)
	if err != nil {
		panic(err)
	}

	r := gin.Default()
	r.POST("/invite_user", inviteUser)
	r.POST("/create_user", createUser)
	r.Run("0.0.0.0:5000")
}

func inviteUser(c *gin.Context) {
	var invitation Invitation
	if err := c.ShouldBindJSON(&invitation); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid request"})
		return
	}

	if !isValidEmail(invitation.Email) {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid email format"})
		return
	}

	var existingInviteID string
	err := db.QueryRow("SELECT invite_id FROM invitations WHERE email = ?", invitation.Email).Scan(&existingInviteID)
	if err == nil {
		c.JSON(http.StatusOK, gin.H{"invite_id": existingInviteID, "message": "Invitation already exists"})
		return
	}

	inviteID := uuid.New().String()
	_, err = db.Exec("INSERT INTO invitations (invite_id, email) VALUES (?, ?)", inviteID, invitation.Email)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"message": "Failed to create invitation"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"invite_id": inviteID, "message": "Invitation created"})
}

func createUser(c *gin.Context) {
	var user User
	if err := c.ShouldBindJSON(&user); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid request"})
		return
	}

	if !isValidUsername(user.Username) {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid username format"})
		return
	}

	if !isValidPassword(user.Password) {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Password must be at least 8 characters long and include uppercase, lowercase, numbers, and special characters"})
		return
	}

	var inviteID string
	err := db.QueryRow("SELECT invite_id FROM invitations WHERE invite_id = ?", user.InviteID).Scan(&inviteID)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"message": "Invalid invite_id"})
		return
	}

	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(user.Password), bcrypt.DefaultCost)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"message": "Failed to create user"})
		return
	}

	_, err = db.Exec("INSERT INTO users (username, password) VALUES (?, ?)", user.Username, hashedPassword)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Failed to create user. Please choose a different username."})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "User created"})
}

func isValidEmail(email string) bool {
	re := regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
	return re.MatchString(email)
}

func isValidUsername(username string) bool {
	re := regexp.MustCompile(`^[a-zA-Z0-9_]{3,20}$`)
	return re.MatchString(username)
}

func isValidPassword(password string) bool {
	if len(password) < 8 {
		return false
	}
	hasUpper := regexp.MustCompile(`[A-Z]`).MatchString(password)
	hasLower := regexp.MustCompile(`[a-z]`).MatchString(password)
	hasNumber := regexp.MustCompile(`[0-9]`).MatchString(password)
	hasSpecial := regexp.MustCompile(`[!@#\$%^&*(),.?":{}|<>]`).MatchString(password)
	return hasUpper && hasLower && hasNumber && hasSpecial
}

func getDatabasePath() string {
	if path := os.Getenv("DATABASE_PATH"); path != "" {
		return path
	}
	return "db.sqlite3"
}