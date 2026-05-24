package main

import (
	"database/sql"
	"fmt"
	"html/template"
	"io/ioutil"
	"net/http"
	"os"
	"path/filepath"
	"regexp"

	"github.com/gin-gonic/gin"
	"github.com/mattn/go-sqlite3"
	"github.com/google/uuid"
)

type Profile struct {
	Username     string `json:"username"`
	ProfilePage  string `json:"profile_page"`
	ProfilePhoto string `json:"profile_photo"`
}

var db *sql.DB

func init() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		panic(err)
	}

	createTableSQL := `CREATE TABLE IF NOT EXISTS profiles (
		username TEXT PRIMARY KEY,
		profile_page TEXT,
		profile_photo TEXT
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		panic(err)
	}

	// Ensure uploads directory exists
	os.MkdirAll("uploads", os.ModePerm)
}

func main() {
	r := gin.Default()

	r.POST("/add_profile", addProfile)
	r.GET("/profile/:username", getProfile)
	r.GET("/profile-photo/:username", getProfilePhoto)

	r.Run("0.0.0.0:5000")
}

func isValidUsername(username string) bool {
	// Simple regex to allow only alphanumeric characters and underscores
	re := regexp.MustCompile(`^[a-zA-Z0-9_]+$`)
	return re.MatchString(username)
}

func sanitizeProfilePage(profilePage string) string {
	// Sanitize the profile page content to prevent XSS
	return template.HTMLEscapeString(profilePage)
}

func addProfile(c *gin.Context) {
	username := c.PostForm("username")
	profilePage := c.PostForm("profile_page")
	file, err := c.FormFile("profile_photo")
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	if username == "" || profilePage == "" || !isValidUsername(username) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	// Validate file type and size
	if file.Size > 2*1024*1024 { // Limit to 2MB
		c.JSON(http.StatusBadRequest, gin.H{"error": "File too large"})
		return
	}

	allowedFileTypes := map[string]bool{
		"image/png":  true,
		"image/jpeg": true,
		"image/gif":  true,
	}

	if !allowedFileTypes[file.Header.Get("Content-Type")] {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid file type"})
		return
	}

	profilePhotoPath := filepath.Join("uploads", uuid.New().String()+filepath.Ext(file.Filename))
	if err := c.SaveUploadedFile(file, profilePhotoPath); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	_, err = db.Exec("INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)", username, sanitizeProfilePage(profilePage), profilePhotoPath)
	if err != nil {
		if sqliteErr, ok := err.(sqlite3.Error); ok && sqliteErr.Code == sqlite3.ErrConstraint {
			c.JSON(http.StatusConflict, gin.H{"error": "Profile already exists"})
			return
		}
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}

	c.JSON(http.StatusCreated, gin.H{"message": "Profile created successfully"})
}

func getProfile(c *gin.Context) {
	username := c.Param("username")
	var profile Profile
	err := db.QueryRow("SELECT profile_page FROM profiles WHERE username = ?", username).Scan(&profile.ProfilePage)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Profile not found"})
		return
	}

	// Sanitize output to prevent XSS
	c.HTML(http.StatusOK, "profile.html", gin.H{"profile_page": template.HTML(sanitizeProfilePage(profile.ProfilePage))})
}

func getProfilePhoto(c *gin.Context) {
	username := c.Param("username")
	var profile Profile
	err := db.QueryRow("SELECT profile_photo FROM profiles WHERE username = ?", username).Scan(&profile.ProfilePhoto)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Profile photo not found"})
		return
	}

	c.File(profile.ProfilePhoto)
}