package main

import (
	"database/sql"
	"net/http"
	"os"
	"path/filepath"
	"regexp"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
)

var db *sql.DB

func init() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		panic(err)
	}

	createTableSQL := `CREATE TABLE IF NOT EXISTS profiles (
		username TEXT PRIMARY KEY,
		profile_page TEXT,
		profile_photo BLOB
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		panic(err)
	}
}

func addProfile(c *gin.Context) {
	username := c.PostForm("username")
	profilePage := c.PostForm("profile_page")
	file, err := c.FormFile("profile_photo")
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	if !regexp.MustCompile(`^[a-zA-Z0-9]{3,20}$`).MatchString(username) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid username"})
		return
	}

	if username == "" || profilePage == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	// Sanitize the HTML content to prevent XSS attacks
	profilePage = regexp.MustCompile(`<[^>]*>`).ReplaceAllString(profilePage, "")

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

	// Save the uploaded file to a temporary location
	profilePhotoPath := filepath.Join("uploads", file.Filename)
	if err := c.SaveUploadedFile(file, profilePhotoPath); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Could not save profile photo"})
		return
	}

	// Read the file into a byte slice
	profilePhoto, err := os.ReadFile(profilePhotoPath)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Could not read profile photo"})
		return
	}

	_, err = db.Exec("INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)", username, profilePage, profilePhoto)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Database error"})
		return
	}

	c.Status(http.StatusCreated)
}

func getProfile(c *gin.Context) {
	username := c.Param("username")
	var profilePage string
	err := db.QueryRow("SELECT profile_page FROM profiles WHERE username=?", username).Scan(&profilePage)
	if err != nil {
		if err == sql.ErrNoRows {
			c.JSON(http.StatusNotFound, gin.H{"error": "Profile not found"})
		} else {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Database error"})
		}
		return
	}
	c.Data(http.StatusOK, "text/html", []byte(profilePage))
}

func getProfilePhoto(c *gin.Context) {
	username := c.Param("username")
	var profilePhoto []byte
	err := db.QueryRow("SELECT profile_photo FROM profiles WHERE username=?", username).Scan(&profilePhoto)
	if err != nil {
		if err == sql.ErrNoRows {
			c.JSON(http.StatusNotFound, gin.H{"error": "Profile photo not found"})
		} else {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Database error"})
		}
		return
	}
	c.Data(http.StatusOK, "image/png", profilePhoto)
}

func main() {
	r := gin.Default()
	r.POST("/add_profile", addProfile)
	r.GET("/profile/:username", getProfile)
	r.GET("/profile-photo/:username", getProfilePhoto)
	r.Run("0.0.0.0:5000")
}