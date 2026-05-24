package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"regexp"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
	"github.com/google/uuid"
)

type Invitation struct {
	Email   string `json:"email"`
	InviteID string `json:"invite_id"`
}

type User struct {
	UserName string `json:"user_name"`
	Password string `json:"password"`
}

var db *sql.DB

func init() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		panic(err)
	}

	createTable := `
	CREATE TABLE IF NOT EXISTS invitations (
		id TEXT PRIMARY KEY,
		email TEXT UNIQUE
	);
	CREATE TABLE IF NOT EXISTS users (
		username TEXT PRIMARY KEY,
		password TEXT
	);`
	_, err = db.Exec(createTable)
	if err != nil {
		panic(err)
	}
}

func main() {
	router := gin.Default()
	router.POST("/invite_user", inviteUser)
	router.POST("/create_user", createUser)
	router.Run("0.0.0.0:5000")
}

func inviteUser(c *gin.Context) {
	var invitation Invitation
	if err := c.ShouldBindJSON(&invitation); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid request body"})
		return
	}

	if !isValidEmail(invitation.Email) {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid email format"})
		return
	}

	var inviteID string
	err := db.QueryRow("SELECT id FROM invitations WHERE email = ?", invitation.Email).Scan(&inviteID)
	if err == nil {
		c.JSON(http.StatusOK, gin.H{"invite_id": inviteID, "message": "Invitation already exists"})
		return
	}

	inviteID = uuid.NewString()
	_, err = db.Exec("INSERT INTO invitations (id, email) VALUES (?, ?)", inviteID, invitation.Email)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"message": "Failed to create invitation"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"invite_id": inviteID, "message": "Invitation created successfully"})
}

func createUser(c *gin.Context) {
	var user User
	if err := c.ShouldBindJSON(&user); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid request body"})
		return
	}

	if len(user.UserName) == 0 || len(user.Password) == 0 {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Username and password are required"})
		return
	}

	var inviteID string
	err := db.QueryRow("SELECT id FROM invitations WHERE id = ?", user.UserName).Scan(&inviteID)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"message": "Invalid invite_id"})
		return
	}

	_, err = db.Exec("INSERT INTO users (username, password) VALUES (?, ?)", user.UserName, user.Password)
	if err != nil {
		if err.Error() == "UNIQUE constraint failed: users.username" {
			c.JSON(http.StatusBadRequest, gin.H{"message": "Username already exists. Try providing a different username."})
			return
		}
		c.JSON(http.StatusInternalServerError, gin.H{"message": "Failed to create user"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "User created successfully"})
}

func isValidEmail(email string) bool {
	re := regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
	return re.MatchString(email)
}