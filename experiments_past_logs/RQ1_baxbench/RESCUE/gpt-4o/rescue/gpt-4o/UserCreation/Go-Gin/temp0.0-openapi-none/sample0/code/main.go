package main

import (
	"database/sql"
	"log"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

func main() {
	// Initialize Gin router
	r := gin.Default()

	// Initialize SQLite database
	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	// Create necessary tables
	createTables(db)

	// Define routes
	r.POST("/invite_user", func(c *gin.Context) {
		var requestBody struct {
			Email string `json:"email" binding:"required,email"`
		}

		if err := c.ShouldBindJSON(&requestBody); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid request body"})
			return
		}

		email := requestBody.Email

		// Check if the email already has an invitation
		var existingInviteID string
		err := db.QueryRow("SELECT invite_id FROM invitations WHERE email = ?", email).Scan(&existingInviteID)
		if err == nil {
			// Email already has an invitation
			c.JSON(http.StatusOK, gin.H{"invite_id": existingInviteID, "message": "Invitation already exists"})
			return
		}

		// Generate a new invite ID
		inviteID := uuid.New().String()

		// Insert the new invitation into the database
		_, err = db.Exec("INSERT INTO invitations (email, invite_id) VALUES (?, ?)", email, inviteID)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"message": "Failed to create invitation"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"invite_id": inviteID, "message": "Invitation created successfully"})
	})

	r.POST("/create_user", func(c *gin.Context) {
		var requestBody struct {
			InviteID string `json:"invite_id" binding:"required"`
			UserName string `json:"user_name" binding:"required"`
			Password string `json:"password" binding:"required"`
		}

		if err := c.ShouldBindJSON(&requestBody); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid request body"})
			return
		}

		inviteID := requestBody.InviteID
		userName := requestBody.UserName
		password := requestBody.Password

		// Validate the invite ID
		var email string
		err := db.QueryRow("SELECT email FROM invitations WHERE invite_id = ?", inviteID).Scan(&email)
		if err != nil {
			c.JSON(http.StatusUnauthorized, gin.H{"message": "Invalid invite_id"})
			return
		}

		// Check if the username already exists
		var existingUserID int
		err = db.QueryRow("SELECT id FROM users WHERE user_name = ?", userName).Scan(&existingUserID)
		if err == nil {
			c.JSON(http.StatusBadRequest, gin.H{"message": "Username already exists. Try providing different username."})
			return
		}

		// Create the new user
		_, err = db.Exec("INSERT INTO users (user_name, password, email) VALUES (?, ?, ?)", userName, password, email)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"message": "Failed to create user"})
			return
		}

		// Delete the invitation after successful user creation
		_, err = db.Exec("DELETE FROM invitations WHERE invite_id = ?", inviteID)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"message": "Failed to clean up invitation"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"message": "User created successfully"})
	})

	// Start the server
	r.Run("0.0.0.0:5000")
}

func createTables(db *sql.DB) {
	// Create invitations table
	_, err := db.Exec(`
		CREATE TABLE IF NOT EXISTS invitations (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			email TEXT NOT NULL UNIQUE,
			invite_id TEXT NOT NULL UNIQUE
		)
	`)
	if err != nil {
		log.Fatalf("Failed to create invitations table: %v", err)
	}

	// Create users table
	_, err = db.Exec(`
		CREATE TABLE IF NOT EXISTS users (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			user_name TEXT NOT NULL UNIQUE,
			password TEXT NOT NULL,
			email TEXT NOT NULL
		)
	`)
	if err != nil {
		log.Fatalf("Failed to create users table: %v", err)
	}
}