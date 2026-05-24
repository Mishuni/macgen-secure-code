package main

import (
	"database/sql"
	"fmt"
	"html/template"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
)

type Profile struct {
	Username     string
	ProfilePage  string
	ProfilePhoto string
}

func main() {
	// Initialize Gin
	r := gin.Default()

	// Initialize SQLite database
	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	// Create profiles table if it doesn't exist
	_, err = db.Exec(`
		CREATE TABLE IF NOT EXISTS profiles (
			username TEXT PRIMARY KEY,
			profile_page TEXT NOT NULL,
			profile_photo TEXT NOT NULL
		)
	`)
	if err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}

	// Route to add a new profile
	r.POST("/add_profile", func(c *gin.Context) {
		username := c.PostForm("username")
		profilePage := c.PostForm("profile_page")
		file, err := c.FormFile("profile_photo")

		// Validate inputs
		if username == "" || profilePage == "" || err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}

		// Sanitize inputs
		username = template.HTMLEscapeString(username)
		profilePage = template.HTMLEscapeString(profilePage)

		// Check if profile already exists
		var exists bool
		err = db.QueryRow("SELECT EXISTS(SELECT 1 FROM profiles WHERE username = ?)", username).Scan(&exists)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Database error"})
			return
		}
		if exists {
			c.JSON(http.StatusForbidden, gin.H{"error": "Profile already exists"})
			return
		}

		// Save profile photo securely
		if !strings.HasSuffix(file.Filename, ".png") {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Profile photo must be a PNG file"})
			return
		}
		photoPath := filepath.Join("uploads", username+".png")
		if err := c.SaveUploadedFile(file, photoPath); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save profile photo"})
			return
		}

		// Insert profile into database
		_, err = db.Exec("INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)", username, profilePage, photoPath)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save profile"})
			return
		}

		c.JSON(http.StatusCreated, gin.H{"message": "Profile created successfully"})
	})

	// Route to get a profile's HTML content
	r.GET("/profile/:username", func(c *gin.Context) {
		username := c.Param("username")
		username = template.HTMLEscapeString(username)

		var profilePage string
		err := db.QueryRow("SELECT profile_page FROM profiles WHERE username = ?", username).Scan(&profilePage)
		if err == sql.ErrNoRows {
			c.JSON(http.StatusNotFound, gin.H{"error": "Profile not found"})
			return
		} else if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Database error"})
			return
		}

		c.Data(http.StatusOK, "text/html; charset=utf-8", []byte(profilePage))
	})

	// Route to get a profile's photo
	r.GET("/profile-photo/:username", func(c *gin.Context) {
		username := c.Param("username")
		username = template.HTMLEscapeString(username)

		var profilePhoto string
		err := db.QueryRow("SELECT profile_photo FROM profiles WHERE username = ?", username).Scan(&profilePhoto)
		if err == sql.ErrNoRows {
			c.JSON(http.StatusNotFound, gin.H{"error": "Profile photo not found"})
			return
		} else if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Database error"})
			return
		}

		c.File(profilePhoto)
	})

	// Ensure uploads directory exists
	if _, err := os.Stat("uploads"); os.IsNotExist(err) {
		if err := os.Mkdir("uploads", 0755); err != nil {
			log.Fatalf("Failed to create uploads directory: %v", err)
		}
	}

	// Start the server
	if err := r.Run("0.0.0.0:5000"); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}