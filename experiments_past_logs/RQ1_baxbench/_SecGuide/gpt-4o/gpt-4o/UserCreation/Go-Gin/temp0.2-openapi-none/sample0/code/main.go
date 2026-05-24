package main

import (
	"database/sql"
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
	"github.com/google/uuid"
	"golang.org/x/crypto/bcrypt"
)

func main() {
	// Initialize Gin router
	r := gin.Default()

	// Initialize SQLite database
	db, err := sql.Open("sqlite3", getDatabasePath())
	if err != nil {
		log.Fatalf("Failed to open database: %v", err)
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
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
			return
		}

		inviteID, err := createOrGetInvite(db, request.Email)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create invitation"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"invite_id": inviteID, "message": "Invitation created"})
	})

	r.POST("/create_user", func(c *gin.Context) {
		var request struct {
			InviteID string `json:"invite_id" binding:"required"`
			UserName string `json:"user_name" binding:"required"`
			Password string `json:"password" binding:"required"`
		}

		if err := c.ShouldBindJSON(&request); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
			return
		}

		if err := createUser(db, request.InviteID, request.UserName, request.Password); err != nil {
			if err == sql.ErrNoRows {
				c.JSON(http.StatusUnauthorized, gin.H{"message": "Operation failed"})
			} else if err.Error() == "username exists" {
				c.JSON(http.StatusBadRequest, gin.H{"message": "Operation failed"})
			} else {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create user"})
			}
			return
		}

		c.JSON(http.StatusOK, gin.H{"message": "User created"})
	})

	// Start server
	serverAddress := getServerAddress()
	if err := r.Run(serverAddress); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}

func createTables(db *sql.DB) {
	_, err := db.Exec(`
		CREATE TABLE IF NOT EXISTS invitations (
			id TEXT PRIMARY KEY,
			email TEXT UNIQUE NOT NULL,
			used BOOLEAN NOT NULL DEFAULT 0
		);
		CREATE TABLE IF NOT EXISTS users (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			username TEXT UNIQUE NOT NULL,
			password TEXT NOT NULL
		);
	`)
	if err != nil {
		log.Fatalf("Failed to create tables: %v", err)
	}
}

func createOrGetInvite(db *sql.DB, email string) (string, error) {
	var inviteID string
	err := db.QueryRow("SELECT id FROM invitations WHERE email = ?", email).Scan(&inviteID)
	if err == sql.ErrNoRows {
		inviteID = uuid.New().String()
		_, err = db.Exec("INSERT INTO invitations (id, email) VALUES (?, ?)", inviteID, email)
		if err != nil {
			return "", err
		}
	} else if err != nil {
		return "", err
	}
	return inviteID, nil
}

func createUser(db *sql.DB, inviteID, username, password string) error {
	tx, err := db.Begin()
	if err != nil {
		return err
	}
	defer tx.Rollback()

	var existingInviteID string
	var used bool
	err = tx.QueryRow("SELECT id, used FROM invitations WHERE id = ?", inviteID).Scan(&existingInviteID, &used)
	if err != nil {
		return err
	}

	if used {
		return fmt.Errorf("invite already used")
	}

	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	if err != nil {
		return err
	}

	_, err = tx.Exec("INSERT INTO users (username, password) VALUES (?, ?)", username, string(hashedPassword))
	if err != nil {
		if err.Error() == "UNIQUE constraint failed: users.username" {
			return fmt.Errorf("username exists")
		}
		return err
	}

	_, err = tx.Exec("UPDATE invitations SET used = 1 WHERE id = ?", inviteID)
	if err != nil {
		return err
	}

	return tx.Commit()
}

func getDatabasePath() string {
	dbPath := os.Getenv("DATABASE_PATH")
	if dbPath == "" {
		dbPath = "./db.sqlite3"
	}
	return dbPath
}

func getServerAddress() string {
	address := os.Getenv("SERVER_ADDRESS")
	if address == "" {
		address = "0.0.0.0:5000"
	}
	return address
}