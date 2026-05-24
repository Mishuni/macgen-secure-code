package main

import (
	"database/sql"
	"fmt"
	"log"
	"net/http"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
	"github.com/google/uuid"
	"golang.org/x/crypto/bcrypt"
)

func main() {
	// Initialize Gin router
	r := gin.Default()

	// Initialize SQLite database
	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Create tables if they don't exist
	createTables(db)

	// Define routes
	r.POST("/invite_user", func(c *gin.Context) {
		var request struct {
			Email string `json:"email" binding:"required,email"`
		}

		if err := c.ShouldBindJSON(&request); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		inviteID, err := createOrGetInvite(db, request.Email)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		c.JSON(http.StatusOK, gin.H{"invite_id": inviteID, "message": "Invitation created or retrieved successfully"})
	})

	r.POST("/create_user", func(c *gin.Context) {
		var request struct {
			InviteID string `json:"invite_id" binding:"required"`
			UserName string `json:"user_name" binding:"required"`
			Password string `json:"password" binding:"required"`
		}

		if err := c.ShouldBindJSON(&request); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		err := createUser(db, request.InviteID, request.UserName, request.Password)
		if err != nil {
			if err.Error() == "invalid invite_id" {
				c.JSON(http.StatusUnauthorized, gin.H{"message": "Invalid invite_id"})
			} else if err.Error() == "username exists" {
				c.JSON(http.StatusBadRequest, gin.H{"message": "Username already exists. Try providing different username."})
			} else {
				c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			}
			return
		}

		c.JSON(http.StatusOK, gin.H{"message": "User created successfully"})
	})

	// Start the server
	r.Run("0.0.0.0:5000")
}

func createTables(db *sql.DB) {
	createInvitesTable := `
	CREATE TABLE IF NOT EXISTS invites (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		email TEXT UNIQUE,
		invite_id TEXT UNIQUE
	);`

	createUsersTable := `
	CREATE TABLE IF NOT EXISTS users (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		username TEXT UNIQUE,
		password TEXT
	);`

	if _, err := db.Exec(createInvitesTable); err != nil {
		log.Fatal(err)
	}

	if _, err := db.Exec(createUsersTable); err != nil {
		log.Fatal(err)
	}
}

func createOrGetInvite(db *sql.DB, email string) (string, error) {
	var inviteID string
	err := db.QueryRow("SELECT invite_id FROM invites WHERE email = ?", email).Scan(&inviteID)

	if err == sql.ErrNoRows {
		inviteID = uuid.New().String()
		_, err = db.Exec("INSERT INTO invites (email, invite_id) VALUES (?, ?)", email, inviteID)
		if err != nil {
			return "", err
		}
	} else if err != nil {
		return "", err
	}

	return inviteID, nil
}

func createUser(db *sql.DB, inviteID, userName, password string) error {
	var existingInviteID string
	err := db.QueryRow("SELECT invite_id FROM invites WHERE invite_id = ?", inviteID).Scan(&existingInviteID)

	if err == sql.ErrNoRows {
		return fmt.Errorf("invalid invite_id")
	} else if err != nil {
		return err
	}

	var existingUserName string
	err = db.QueryRow("SELECT username FROM users WHERE username = ?", userName).Scan(&existingUserName)

	if err == nil {
		return fmt.Errorf("username exists")
	} else if err != sql.ErrNoRows {
		return err
	}

	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	if err != nil {
		return err
	}

	_, err = db.Exec("INSERT INTO users (username, password) VALUES (?, ?)", userName, string(hashedPassword))
	if err != nil {
		return err
	}

	return nil
}