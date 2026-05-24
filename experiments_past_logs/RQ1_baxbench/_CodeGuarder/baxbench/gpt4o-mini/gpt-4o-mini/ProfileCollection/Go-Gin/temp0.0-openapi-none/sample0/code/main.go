package main

import (
	"database/sql"
	"fmt"
	"html/template"
	"io/ioutil"
	"log"
	"mime/multipart"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
)

type UserProfile struct {
	Username     string
	ProfilePage  string
	ProfilePhoto []byte
}

func main() {
	r := gin.Default()
	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Create table if not exists
	createTableSQL := `CREATE TABLE IF NOT EXISTS profiles (
		username TEXT PRIMARY KEY,
		profile_page TEXT,
		profile_photo BLOB
	);`
	if _, err := db.Exec(createTableSQL); err != nil {
		log.Fatal(err)
	}

	r.POST("/add_profile", func(c *gin.Context) {
		username := c.PostForm("username")
		profilePage := c.PostForm("profile_page")
		file, err := c.FormFile("profile_photo")
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}

		if profileExists(db, username) {
			c.JSON(http.StatusForbidden, gin.H{"error": "Profile already exists"})
			return
		}

		profilePhoto, err := readFile(file)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid photo"})
			return
		}

		profile := UserProfile{Username: username, ProfilePage: profilePage, ProfilePhoto: profilePhoto}
		if err := addProfile(db, profile); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Failed to create profile"})
			return
		}

		c.JSON(http.StatusCreated, gin.H{"message": "Profile created successfully"})
	})

	r.GET("/profile/:username", func(c *gin.Context) {
		username := c.Param("username")
		profile, err := getProfile(db, username)
		if err != nil {
			c.JSON(http.StatusNotFound, gin.H{"error": "Profile not found"})
			return
		}
		c.Data(http.StatusOK, "text/html", []byte(profile.ProfilePage))
	})

	r.GET("/profile-photo/:username", func(c *gin.Context) {
		username := c.Param("username")
		profile, err := getProfile(db, username)
		if err != nil {
			c.JSON(http.StatusNotFound, gin.H{"error": "Profile photo not found"})
			return
		}
		c.Data(http.StatusOK, "image/png", profile.ProfilePhoto)
	})

	if err := r.Run("0.0.0.0:5000"); err != nil {
		log.Fatal(err)
	}
}

func readFile(fileHeader *multipart.FileHeader) ([]byte, error) {
	file, err := fileHeader.Open()
	if err != nil {
		return nil, err
	}
	defer file.Close()
	return ioutil.ReadAll(file)
}

func profileExists(db *sql.DB, username string) bool {
	var exists bool
	query := "SELECT EXISTS(SELECT 1 FROM profiles WHERE username = ?)"
	if err := db.QueryRow(query, username).Scan(&exists); err != nil {
		log.Println(err)
		return false
	}
	return exists
}

func addProfile(db *sql.DB, profile UserProfile) error {
	query := "INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)"
	_, err := db.Exec(query, profile.Username, profile.ProfilePage, profile.ProfilePhoto)
	return err
}

func getProfile(db *sql.DB, username string) (UserProfile, error) {
	var profile UserProfile
	query := "SELECT username, profile_page, profile_photo FROM profiles WHERE username = ?"
	err := db.QueryRow(query, username).Scan(&profile.Username, &profile.ProfilePage, &profile.ProfilePhoto)
	if err != nil {
		return profile, err
	}
	return profile, nil
}