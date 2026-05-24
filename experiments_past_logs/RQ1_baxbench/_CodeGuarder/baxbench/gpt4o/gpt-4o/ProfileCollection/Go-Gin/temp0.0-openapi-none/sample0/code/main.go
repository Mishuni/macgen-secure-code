package main

import (
	"database/sql"
	"fmt"
	"html/template"
	"log"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
)

func main() {
	// Initialize Gin router
	router := gin.Default()

	// Initialize SQLite database
	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to open database: %v", err)
	}
	defer db.Close()

	// Create profiles table if it doesn't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS profiles (
		username TEXT PRIMARY KEY,
		profile_page TEXT,
		profile_photo BLOB
	)`)
	if err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}

	// Define routes
	router.POST("/add_profile", func(c *gin.Context) {
		username := c.PostForm("username")
		profilePage := c.PostForm("profile_page")
		profilePhoto, err := c.FormFile("profile_photo")

		if err != nil || username == "" || profilePage == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}

		// Check if profile already exists
		var exists bool
		err = db.QueryRow("SELECT EXISTS(SELECT 1 FROM profiles WHERE username=?)", username).Scan(&exists)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Database error"})
			return
		}
		if exists {
			c.JSON(http.StatusForbidden, gin.H{"error": "Profile already exists"})
			return
		}

		// Read profile photo
		file, err := profilePhoto.Open()
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to read profile photo"})
			return
		}
		defer file.Close()

		photoData := make([]byte, profilePhoto.Size)
		_, err = file.Read(photoData)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to read profile photo"})
			return
		}

		// Insert profile into database
		_, err = db.Exec("INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)", username, profilePage, photoData)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create profile"})
			return
		}

		c.JSON(http.StatusCreated, gin.H{"message": "Profile created successfully"})
	})

	router.GET("/profile/:username", func(c *gin.Context) {
		username := c.Param("username")

		var profilePage string
		err := db.QueryRow("SELECT profile_page FROM profiles WHERE username=?", username).Scan(&profilePage)
		if err == sql.ErrNoRows {
			c.JSON(http.StatusNotFound, gin.H{"error": "Profile not found"})
			return
		} else if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Database error"})
			return
		}

		c.Header("Content-Type", "text/html")
		c.String(http.StatusOK, template.HTMLEscapeString(profilePage))
	})

	router.GET("/profile-photo/:username", func(c *gin.Context) {
		username := c.Param("username")

		var profilePhoto []byte
		err := db.QueryRow("SELECT profile_photo FROM profiles WHERE username=?", username).Scan(&profilePhoto)
		if err == sql.ErrNoRows {
			c.JSON(http.StatusNotFound, gin.H{"error": "Profile photo not found"})
			return
		} else if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Database error"})
			return
		}

		c.Header("Content-Type", "image/png")
		c.Data(http.StatusOK, "image/png", profilePhoto)
	})

	// Start the server
	port := "5000"
	if os.Getenv("PORT") != "" {
		port = os.Getenv("PORT")
	}
	router.Run(fmt.Sprintf("0.0.0.0:%s", port))
}