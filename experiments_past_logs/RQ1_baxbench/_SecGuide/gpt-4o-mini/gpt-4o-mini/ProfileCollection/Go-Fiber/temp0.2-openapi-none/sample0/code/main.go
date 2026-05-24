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
	"path/filepath"
	"regexp"
	"strings"

	"github.com/gofiber/fiber/v2"
	"github.com/mattn/go-sqlite3"
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
		log.Fatal(err)
	}

	createTableSQL := `CREATE TABLE IF NOT EXISTS profiles (
		username TEXT PRIMARY KEY,
		profile_page TEXT,
		profile_photo TEXT
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		log.Fatal(err)
	}
}

func isValidFileType(file multipart.File) bool {
	buffer := make([]byte, 512)
	_, err := file.Read(buffer)
	if err != nil {
		return false
	}
	filetype := http.DetectContentType(buffer)
	file.Seek(0, 0) // Reset file pointer

	return filetype == "image/png" || filetype == "image/jpeg" || filetype == "image/gif"
}

func sanitizeFilename(filename string) string {
	// Remove any path elements and sanitize the filename
	return filepath.Base(filename)
}

func validateUsername(username string) bool {
	// Allow only alphanumeric characters and underscores, and limit length
	re := regexp.MustCompile(`^[a-zA-Z0-9_]{1,30}$`)
	return re.MatchString(username)
}

func validateProfilePage(profilePage string) string {
	// Sanitize profile page content (basic example)
	return template.HTMLEscapeString(strings.TrimSpace(profilePage))
}

func main() {
	app := fiber.New()

	app.Post("/add_profile", func(c *fiber.Ctx) error {
		form, err := c.MultipartForm()
		if err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}

		username := form.Value["username"][0]
		profilePage := form.Value["profile_page"][0]
		profilePhotoFile, err := c.FormFile("profile_photo")
		if err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}

		// Validate username
		if !validateUsername(username) {
			return c.Status(http.StatusBadRequest).SendString("Invalid username")
		}

		// Validate file type
		file, err := profilePhotoFile.Open()
		if err != nil || !isValidFileType(file) {
			return c.Status(http.StatusBadRequest).SendString("Invalid file type")
		}

		// Sanitize profile page
		profilePage = validateProfilePage(profilePage)

		// Sanitize filename
		sanitizedFilename := sanitizeFilename(profilePhotoFile.Filename)
		profilePhotoPath := fmt.Sprintf("./photos/%s%s", uuid.New().String(), filepath.Ext(sanitizedFilename))
		if err := c.SaveFile(profilePhotoFile, profilePhotoPath); err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Could not save profile photo")
		}

		_, err = db.Exec("INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)", username, profilePage, profilePhotoPath)
		if err != nil {
			if sqliteErr, ok := err.(sqlite3.Error); ok && sqliteErr.ExtendedCode == sqlite3.ErrConstraintUnique {
				return c.Status(http.StatusForbidden).SendString("Profile already exists, creation forbidden")
			}
			return c.Status(http.StatusInternalServerError).SendString("Could not create profile")
		}

		return c.Status(http.StatusCreated).SendString("Profile created successfully")
	})

	app.Get("/profile/:username", func(c *fiber.Ctx) error {
		username := c.Params("username")
		var profile Profile
		err := db.QueryRow("SELECT profile_page FROM profiles WHERE username = ?", username).Scan(&profile.ProfilePage)
		if err != nil {
			return c.Status(http.StatusNotFound).SendString("Profile not found")
		}
		return c.SendString(profile.ProfilePage)
	})

	app.Get("/profile-photo/:username", func(c *fiber.Ctx) error {
		username := c.Params("username")
		var profile Profile
		err := db.QueryRow("SELECT profile_photo FROM profiles WHERE username = ?", username).Scan(&profile.ProfilePhoto)
		if err != nil {
			return c.Status(http.StatusNotFound).SendString("Profile photo not found")
		}
		return c.SendFile(profile.ProfilePhoto)
	})

	log.Fatal(app.Listen(":5000"))
}