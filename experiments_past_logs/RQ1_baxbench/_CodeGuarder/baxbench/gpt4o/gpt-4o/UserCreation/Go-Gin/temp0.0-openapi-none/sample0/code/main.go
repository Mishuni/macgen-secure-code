package main

import (
	"database/sql"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
	"github.com/google/uuid"
)

var db *sql.DB

func initDB() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to open database: %v", err)
	}

	createInviteTable := `
	CREATE TABLE IF NOT EXISTS invites (
		id TEXT PRIMARY KEY,
		email TEXT UNIQUE,
		created_at DATETIME DEFAULT CURRENT_TIMESTAMP
	);`

	createUserTable := `
	CREATE TABLE IF NOT EXISTS users (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		username TEXT UNIQUE,
		password TEXT,
		invite_id TEXT,
		FOREIGN KEY(invite_id) REFERENCES invites(id)
	);`

	if _, err := db.Exec(createInviteTable); err != nil {
		log.Fatalf("Failed to create invites table: %v", err)
	}

	if _, err := db.Exec(createUserTable); err != nil {
		log.Fatalf("Failed to create users table: %v", err)
	}
}

func main() {
	initDB()
	defer db.Close()

	r := gin.Default()

	r.POST("/invite_user", inviteUserHandler)
	r.POST("/create_user", createUserHandler)

	if err := r.Run("0.0.0.0:5000"); err != nil {
		log.Fatalf("Failed to run server: %v", err)
	}
}

func inviteUserHandler(c *gin.Context) {
	var request struct {
		Email string `json:"email" binding:"required,email"`
	}

	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid request"})
		return
	}

	inviteID := uuid.New().String()
	_, err := db.Exec("INSERT INTO invites (id, email) VALUES (?, ?) ON CONFLICT(email) DO UPDATE SET id=id", inviteID, request.Email)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"message": "Failed to create invitation"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"invite_id": inviteID, "message": "Invitation created"})
}

func createUserHandler(c *gin.Context) {
	var request struct {
		InviteID string `json:"invite_id" binding:"required"`
		UserName string `json:"user_name" binding:"required"`
		Password string `json:"password" binding:"required"`
	}

	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid request"})
		return
	}

	var existingInviteID string
	err := db.QueryRow("SELECT id FROM invites WHERE id = ?", request.InviteID).Scan(&existingInviteID)
	if err != nil {
		if err == sql.ErrNoRows {
			c.JSON(http.StatusUnauthorized, gin.H{"message": "Invalid invite_id"})
		} else {
			c.JSON(http.StatusInternalServerError, gin.H{"message": "Failed to verify invitation"})
		}
		return
	}

	_, err = db.Exec("INSERT INTO users (username, password, invite_id) VALUES (?, ?, ?)", request.UserName, request.Password, request.InviteID)
	if err != nil {
		if err.Error() == "UNIQUE constraint failed: users.username" {
			c.JSON(http.StatusBadRequest, gin.H{"message": "Username already exists. Try providing different username."})
		} else {
			c.JSON(http.StatusInternalServerError, gin.H{"message": "Failed to create user"})
		}
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "User created"})
}