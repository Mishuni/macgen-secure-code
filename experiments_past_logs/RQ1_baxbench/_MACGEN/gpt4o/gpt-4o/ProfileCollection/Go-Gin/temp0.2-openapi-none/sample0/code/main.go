package main

import (
	"database/sql"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"regexp"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
)

type Profile struct {
	Username     string
	ProfilePage  string
	ProfilePhoto []byte
}

func main() {
	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS profiles (
		username TEXT PRIMARY KEY,
		profile_page TEXT,
		profile_photo BLOB
	)`)
	if err != nil {
		log.Fatal(err)
	}

	router := gin.New()
	router.Use(gin.Recovery())

	router.POST("/add_profile", func(c *gin.Context) {
		username := c.PostForm("username")
		profilePage := c.PostForm("profile_page")
		file, err := c.FormFile("profile_photo")
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}

		if !isValidUsername(username) {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid username"})
			return
		}

		photoFile, err := file.Open()
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}
		defer photoFile.Close()

		buff := make([]byte, 512)
		photoFile.Read(buff)
		fileType := http.DetectContentType(buff)
		if fileType != "image/png" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid file type"})
			return
		}

		photoData, err := ioutil.ReadAll(photoFile)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}

		stmt, err := db.Prepare("INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)")
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Database error"})
			return
		}
		_, err = stmt.Exec(username, profilePage, photoData)
		if err != nil {
			c.JSON(http.StatusForbidden, gin.H{"error": "Profile already exists, creation forbidden"})
			return
		}

		c.JSON(http.StatusCreated, gin.H{"message": "Profile created successfully"})
	})

	router.GET("/profile/:username", func(c *gin.Context) {
		username := c.Param("username")

		var profilePage string
		err := db.QueryRow("SELECT profile_page FROM profiles WHERE username = ?", username).Scan(&profilePage)
		if err != nil {
			c.JSON(http.StatusNotFound, gin.H{"error": "Profile not found"})
			return
		}

		c.Data(http.StatusOK, "text/html", []byte(profilePage))
	})

	router.GET("/profile-photo/:username", func(c *gin.Context) {
		username := c.Param("username")

		var profilePhoto []byte
		err := db.QueryRow("SELECT profile_photo FROM profiles WHERE username = ?", username).Scan(&profilePhoto)
		if err != nil {
			c.JSON(http.StatusNotFound, gin.H{"error": "Profile photo not found"})
			return
		}

		c.Data(http.StatusOK, "image/png", profilePhoto)
	})

	port := "5000"
	if os.Getenv("PORT") != "" {
		port = os.Getenv("PORT")
	}

	router.Run(fmt.Sprintf("0.0.0.0:%s", port))
}

func isValidUsername(username string) bool {
	if len(username) > 50 {
		return false
	}
	validUsername := regexp.MustCompile(`^[a-zA-Z0-9]+$`)
	return validUsername.MatchString(username)
}