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
)

var db *sql.DB

type Invitation struct {
	Email    string `json:"email"`
	InviteID string `json:"invite_id"`
}

type User struct {
	UserName string `json:"user_name"`
	Password string `json:"password"`
	InviteID string `json:"invite_id"`
}

func main() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		panic(err)
	}
	defer db.Close()

	createTable()

	router := gin.Default()
	router.POST("/invite_user", inviteUser)
	router.POST("/create_user", createUser)
	router.Run("0.0.0.0:5000")
}

func createTable() {
	query := `
	CREATE TABLE IF NOT EXISTS invitations (
		id TEXT PRIMARY KEY,
		email TEXT UNIQUE
	);
	CREATE TABLE IF NOT EXISTS users (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		username TEXT UNIQUE,
		password TEXT,
		invite_id TEXT,
		FOREIGN KEY (invite_id) REFERENCES invitations(id)
	);`
	_, err := db.Exec(query)
	if err != nil {
		panic(err)
	}
}

func isValidEmail(email string) bool {
	re := regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
	return re.MatchString(email)
}

func isValidUserName(username string) bool {
	re := regexp.MustCompile(`^[a-zA-Z0-9]{3,20}$`)
	return re.MatchString(username)
}

func inviteUser(c *gin.Context) {
	var invitation Invitation
	if err := c.ShouldBindJSON(&invitation); err != nil || !isValidEmail(invitation.Email) {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid email format"})
		return
	}

	var existingID string
	err := db.QueryRow("SELECT id FROM invitations WHERE email = ?", invitation.Email).Scan(&existingID)
	if err == nil {
		c.JSON(http.StatusOK, gin.H{"invite_id": existingID, "message": "Invitation already exists"})
		return
	}

	inviteID := uuid.New().String()
	_, err = db.Exec("INSERT INTO invitations (id, email) VALUES (?, ?)", inviteID, invitation.Email)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"message": "Failed to create invitation"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"invite_id": inviteID, "message": "Invitation created"})
}

func createUser(c *gin.Context) {
	var user User
	if err := c.ShouldBindJSON(&user); err != nil || !isValidUserName(user.UserName) {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid username format"})
		return
	}

	var inviteID string
	err := db.QueryRow("SELECT id FROM invitations WHERE id = ?", user.InviteID).Scan(&inviteID)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"message": "Invalid invite_id"})
		return
	}

	_, err = db.Exec("INSERT INTO users (username, password, invite_id) VALUES (?, ?, ?)", user.UserName, user.Password, user.InviteID)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Username already exists. Try providing different username."})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "User created"})
}