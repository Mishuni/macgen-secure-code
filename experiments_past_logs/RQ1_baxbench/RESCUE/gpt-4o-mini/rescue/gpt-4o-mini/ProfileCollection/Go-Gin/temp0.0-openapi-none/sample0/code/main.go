package main

import (
	"fmt"
	"html/template"
	"io/ioutil"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
	"github.com/mattn/go-sqlite3"
)

type Profile struct {
	Username     string `json:"username"`
	ProfilePage  string `json:"profile_page"`
	ProfilePhoto string `json:"profile_photo"`
}

func main() {
	r := gin.Default()
	db, err := initDB()
	if err != nil {
		panic(err)
	}
	defer db.Close()

	r.POST("/add_profile", func(c *gin.Context) {
		var profile Profile

		// Parse the multipart form
		if err := c.ShouldBindMultipart(&profile); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}

		// Check if the profile already exists
		var exists bool
		err = db.QueryRow("SELECT EXISTS(SELECT 1 FROM profiles WHERE username = ?)", profile.Username).Scan(&exists)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Database error"})
			return
		}
		if exists {
			c.JSON(http.StatusForbidden, gin.H{"error": "Profile already exists, creation forbidden"})
			return
		}

		// Save the profile page
		if err := saveProfilePage(profile.Username, profile.ProfilePage); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save profile page"})
			return
		}

		// Save the profile photo
		if err := saveProfilePhoto(profile.Username, profile.ProfilePhoto); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save profile photo"})
			return
		}

		// Insert profile into the database
		_, err = db.Exec("INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)", profile.Username, profile.ProfilePage, profile.ProfilePhoto)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Database error"})
			return
		}

		c.JSON(http.StatusCreated, gin.H{"message": "Profile created successfully"})
	})

	r.GET("/profile/:username", func(c *gin.Context) {
		username := c.Param("username")
		var profilePage string

		err := db.QueryRow("SELECT profile_page FROM profiles WHERE username = ?", username).Scan(&profilePage)
		if err != nil {
			if err == sqlite3.ErrNoRows {
				c.JSON(http.StatusNotFound, gin.H{"error": "Profile not found"})
			} else {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Database error"})
			}
			return
		}

		c.Data(http.StatusOK, "text/html", []byte(profilePage))
	})

	r.GET("/profile-photo/:username", func(c *gin.Context) {
		username := c.Param("username")
		profilePhoto, err := ioutil.ReadFile(fmt.Sprintf("photos/%s.png", username))
		if err != nil {
			c.JSON(http.StatusNotFound, gin.H{"error": "Profile photo not found"})
			return
		}

		c.Data(http.StatusOK, "image/png", profilePhoto)
	})

	r.Run("0.0.0.0:5000")
}

func initDB() (*sql.DB, error) {
	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		return nil, err
	}

	// Create the profiles table if it doesn't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS profiles (
		username TEXT PRIMARY KEY,
		profile_page TEXT,
		profile_photo TEXT
	)`)
	if err != nil {
		return nil, err
	}

	return db, nil
}

func saveProfilePage(username, content string) error {
	return ioutil.WriteFile(fmt.Sprintf("pages/%s.html", username), []byte(content), 0644)
}

func saveProfilePhoto(username, photo string) error {
	return ioutil.WriteFile(fmt.Sprintf("photos/%s.png", username), []byte(photo), 0644)
}