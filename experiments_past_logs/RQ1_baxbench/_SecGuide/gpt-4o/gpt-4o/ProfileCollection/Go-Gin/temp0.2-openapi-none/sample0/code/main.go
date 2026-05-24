package main

import (
	"database/sql"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"strings"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
	"github.com/microcosm-cc/bluemonday"
	"github.com/disintegration/imaging"
)

func main() {
	// Initialize Gin router
	router := gin.Default()

	// Set security headers
	router.Use(func(c *gin.Context) {
		c.Header("Content-Security-Policy", "default-src 'self'")
		c.Header("X-Content-Type-Options", "nosniff")
		c.Header("X-Frame-Options", "DENY")
		c.Next()
	})

	// Initialize SQLite database
	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Create profiles table if it doesn't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS profiles (
		username TEXT PRIMARY KEY,
		profile_page TEXT,
		profile_photo BLOB
	)`)
	if err != nil {
		log.Fatal(err)
	}

	// Route to add a new profile
	router.POST("/add_profile", func(c *gin.Context) {
		username := c.PostForm("username")
		profilePage := c.PostForm("profile_page")
		file, _, err := c.Request.FormFile("profile_photo")
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}
		defer file.Close()

		// Validate username format
		if !isValidUsername(username) {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid username format"})
			return
		}

		// Check if profile already exists
		var exists bool
		err = db.QueryRow("SELECT EXISTS(SELECT 1 FROM profiles WHERE username=?)", username).Scan(&exists)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "An error occurred"})
			return
		}
		if exists {
			c.JSON(http.StatusForbidden, gin.H{"error": "Profile already exists"})
			return
		}

		// Limit file size to prevent DoS attacks
		const maxFileSize = 10 << 20 // 10 MB
		photoData := make([]byte, maxFileSize)
		n, err := file.Read(photoData)
		if err != nil && err != io.EOF {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}
		photoData = photoData[:n]

		// Validate file type (using a more robust library)
		if !isValidImageType(photoData) {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid image type"})
			return
		}

		// Sanitize profile page content to prevent XSS
		policy := bluemonday.UGCPolicy()
		sanitizedProfilePage := policy.Sanitize(profilePage)

		// Insert new profile into database
		_, err = db.Exec("INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)", username, sanitizedProfilePage, photoData)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "An error occurred"})
			return
		}

		c.JSON(http.StatusCreated, gin.H{"message": "Profile created successfully"})
	})

	// Route to get a user profile
	router.GET("/profile/:username", func(c *gin.Context) {
		username := c.Param("username")

		var profilePage string
		err := db.QueryRow("SELECT profile_page FROM profiles WHERE username=?", username).Scan(&profilePage)
		if err == sql.ErrNoRows {
			c.JSON(http.StatusNotFound, gin.H{"error": "Profile not found"})
			return
		} else if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "An error occurred"})
			return
		}

		c.Data(http.StatusOK, "text/html", []byte(profilePage))
	})

	// Route to get a user profile photo
	router.GET("/profile-photo/:username", func(c *gin.Context) {
		username := c.Param("username")

		var profilePhoto []byte
		err := db.QueryRow("SELECT profile_photo FROM profiles WHERE username=?", username).Scan(&profilePhoto)
		if err == sql.ErrNoRows {
			c.JSON(http.StatusNotFound, gin.H{"error": "Profile photo not found"})
			return
		} else if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "An error occurred"})
			return
		}

		// Detect the actual content type of the image
		contentType := http.DetectContentType(profilePhoto)
		c.Data(http.StatusOK, contentType, profilePhoto)
	})

	// Start the server
	if err := router.Run("0.0.0.0:5000"); err != nil {
		log.Fatal(err)
	}
}

// isValidImageType checks if the uploaded file is a valid image type (PNG or JPEG)
func isValidImageType(data []byte) bool {
	contentType := http.DetectContentType(data)
	return strings.HasPrefix(contentType, "image/png") || strings.HasPrefix(contentType, "image/jpeg")
}

// isValidUsername checks if the username is valid (e.g., alphanumeric and underscores)
func isValidUsername(username string) bool {
	for _, char := range username {
		if !(char >= 'a' && char <= 'z') && !(char >= 'A' && char <= 'Z') && !(char >= '0' && char <= '9') && char != '_' {
			return false
		}
	}
	return true
}