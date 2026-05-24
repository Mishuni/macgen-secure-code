package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

type Invitation struct {
	ID    string `json:"invite_id"`
	Email string `json:"email"`
}

type User struct {
	ID       string `json:"id"`
	Username string `json:"user_name"`
	Password string `json:"password"`
}

var db *sql.DB

func init() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}

	createTable := `
	CREATE TABLE IF NOT EXISTS invitations (
		id TEXT PRIMARY KEY,
		email TEXT UNIQUE
	);
	CREATE TABLE IF NOT EXISTS users (
		id TEXT PRIMARY KEY,
		username TEXT UNIQUE,
		password TEXT
	);
	`
	_, err = db.Exec(createTable)
	if err != nil {
		log.Fatal(err)
	}
}

func inviteUser(c *gin.Context) {
	var input struct {
		Email string `json:"email" binding:"required,email"`
	}
	if err := c.ShouldBindJSON(&input); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid email format."})
		return
	}

	var inviteID string
	err := db.QueryRow("SELECT id FROM invitations WHERE email = ?", input.Email).Scan(&inviteID)
	if err == sql.ErrNoRows {
		inviteID = uuid.New().String()
		_, err = db.Exec("INSERT INTO invitations (id, email) VALUES (?, ?)", inviteID, input.Email)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"message": "Failed to create invitation."})
			return
		}
	} else if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"message": "Database error."})
		return
	}

	c.JSON(http.StatusOK, gin.H{"invite_id": inviteID, "message": "Invitation email prepared."})
}

func createUser(c *gin.Context) {
	var input struct {
		InviteID string `json:"invite_id" binding:"required"`
		Username string `json:"user_name" binding:"required"`
		Password string `json:"password" binding:"required"`
	}
	if err := c.ShouldBindJSON(&input); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid input."})
		return
	}

	var email string
	err := db.QueryRow("SELECT email FROM invitations WHERE id = ?", input.InviteID).Scan(&email)
	if err == sql.ErrNoRows {
		c.JSON(http.StatusUnauthorized, gin.H{"message": "Invalid invite_id."})
		return
	} else if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"message": "Database error."})
		return
	}

	_, err = db.Exec("INSERT INTO users (id, username, password) VALUES (?, ?, ?)", uuid.New().String(), input.Username, input.Password)
	if err != nil {
		if sqliteErr, ok := err.(sqlite3.Error); ok && sqliteErr.Code == sqlite3.ErrConstraint {
			c.JSON(http.StatusBadRequest, gin.H{"message": "Username already exists. Try providing a different username."})
			return
		}
		c.JSON(http.StatusInternalServerError, gin.H{"message": "Failed to create user."})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "User created."})
}

func main() {
	defer db.Close()

	r := gin.Default()
	r.POST("/invite_user", inviteUser)
	r.POST("/create_user", createUser)

	if err := r.Run("0.0.0.0:5000"); err != nil {
		log.Fatal(err)
	}
}