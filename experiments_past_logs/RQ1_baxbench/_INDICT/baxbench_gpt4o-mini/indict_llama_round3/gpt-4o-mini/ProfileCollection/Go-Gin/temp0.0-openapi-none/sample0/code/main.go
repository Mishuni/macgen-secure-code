package main

import (
	"database/sql"
	"fmt"
	"html/template"
	"net/http"
	"os"
	"path/filepath"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
	"github.com/google/uuid"
)

type Profile struct {
	Username     string
	ProfilePage  string
	ProfilePhoto string
}

var db *sql.DB

func init() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		panic(err)
	}

	createTableSQL := `CREATE TABLE IF NOT EXISTS profiles (
		"username" TEXT NOT NULL PRIMARY KEY,
		"profile_page" TEXT NOT NULL,
		"profile_photo" TEXT NOT NULL
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		panic(err)
	}
}

func main() {
	r := gin.Default()

	r.POST("/add_profile", addProfile)
	r.GET("/profile/:username", getProfile)
	r.GET("/profile-photo/:username", getProfilePhoto)

	r.Run("0.0.0.0:5000")
}

func addProfile(c *gin.Context) {
	username := c.PostForm("username")
	profilePage := c.PostForm("profile_page")
	file, err := c.FormFile("profile_photo")
	if err != nil || file.Header.Get("Content-Type") != "image/png" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	if username == "" || profilePage == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	profilePhotoPath := fmt.Sprintf("./photos/%s.png", uuid.New().String())
	if err := c.SaveUploadedFile(file, profilePhotoPath); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	if err := saveProfile(Profile{Username: username, ProfilePage: profilePage, ProfilePhoto: profilePhotoPath}); err != nil {
		c.JSON(http.StatusForbidden, gin.H{"error": "Profile already exists, creation forbidden"})
		return
	}

	c.Status(http.StatusCreated)
}

func getProfile(c *gin.Context) {
	username := c.Param("username")
	profile, err := fetchProfile(username)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Profile not found"})
		return
	}

	c.Data(http.StatusOK, "text/html", []byte(profile.ProfilePage))
}

func getProfilePhoto(c *gin.Context) {
	username := c.Param("username")
	profile, err := fetchProfile(username)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Profile photo not found"})
		return
	}

	c.File(profile.ProfilePhoto)
}

func saveProfile(profile Profile) error {
	_, err := db.Exec("INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)", profile.Username, profile.ProfilePage, profile.ProfilePhoto)
	return err
}

func fetchProfile(username string) (Profile, error) {
	var profile Profile
	err := db.QueryRow("SELECT username, profile_page, profile_photo FROM profiles WHERE username = ?", username).Scan(&profile.Username, &profile.ProfilePage, &profile.ProfilePhoto)
	return profile, err
}