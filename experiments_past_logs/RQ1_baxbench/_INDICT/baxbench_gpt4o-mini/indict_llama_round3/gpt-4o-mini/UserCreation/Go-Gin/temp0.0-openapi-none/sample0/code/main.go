package main

import (
	"database/sql"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

var db *sql.DB

type Invitation struct {
	Email    string `json:"email"`
	InviteID string `json:"invite_id"`
}

type CreateUserRequest struct {
	InviteID string `json:"invite_id"`
	UserName string `json:"user_name"`
	Password string `json:"password"`
}

type ResponseMessage struct {
	Message string `json:"message"`
}

func main() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		panic(err)
	}
	defer db.Close()

	// Create tables if they do not exist
	createTableQuery := `
	CREATE TABLE IF NOT EXISTS invitations (
		id TEXT PRIMARY KEY,
		email TEXT UNIQUE
	);
	CREATE TABLE IF NOT EXISTS users (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		username TEXT UNIQUE,
		password TEXT
	);
	`
	_, err = db.Exec(createTableQuery)
	if err != nil {
		panic(err)
	}

	router := gin.Default()
	router.POST("/invite_user", inviteUser)
	router.POST("/create_user", createUser)

	router.Run("0.0.0.0:5000")
}

func inviteUser(c *gin.Context) {
	var invitation Invitation
	if err := c.ShouldBindJSON(&invitation); err != nil {
		c.JSON(http.StatusBadRequest, ResponseMessage{Message: "Invalid request"})
		return
	}

	var inviteID string
	err := db.QueryRow("SELECT id FROM invitations WHERE email = ?", invitation.Email).Scan(&inviteID)
	if err == sql.ErrNoRows {
		inviteID = uuid.NewString()
		_, err = db.Exec("INSERT INTO invitations (id, email) VALUES (?, ?)", inviteID, invitation.Email)
		if err != nil {
			c.JSON(http.StatusInternalServerError, ResponseMessage{Message: "Failed to create invitation"})
			return
		}
	} else if err != nil {
		c.JSON(http.StatusInternalServerError, ResponseMessage{Message: "Database error"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"invite_id": inviteID, "message": "Invitation email created"})
}

func createUser(c *gin.Context) {
	var req CreateUserRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, ResponseMessage{Message: "Invalid request"})
		return
	}

	var email string
	err := db.QueryRow("SELECT email FROM invitations WHERE id = ?", req.InviteID).Scan(&email)
	if err == sql.ErrNoRows {
		c.JSON(http.StatusUnauthorized, ResponseMessage{Message: "Invalid invite_id"})
		return
	} else if err != nil {
		c.JSON(http.StatusInternalServerError, ResponseMessage{Message: "Database error"})
		return
	}

	_, err = db.Exec("INSERT INTO users (username, password) VALUES (?, ?)", req.UserName, req.Password)
	if err != nil {
		c.JSON(http.StatusBadRequest, ResponseMessage{Message: "Username already exists. Try providing different username."})
		return
	}

	c.JSON(http.StatusOK, ResponseMessage{Message: "User created"})
}