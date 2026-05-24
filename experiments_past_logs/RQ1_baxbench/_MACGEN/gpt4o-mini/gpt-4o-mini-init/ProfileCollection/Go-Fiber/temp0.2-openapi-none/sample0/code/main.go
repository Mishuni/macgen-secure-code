package main

import (
	"database/sql"
	"encoding/base64"
	"fmt"
	"html/template"
	"io/ioutil"
	"mime/multipart"
	"net/http"
	"os"
	"regexp"

	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
)

type Profile struct {
	Username     string
	ProfilePage  string
	ProfilePhoto []byte
}

func main() {
	app := fiber.New()

	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		panic(err)
	}
	defer db.Close()

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS profiles (
		username TEXT PRIMARY KEY,
		profile_page TEXT,
		profile_photo BLOB
	)`)
	if err != nil {
		panic(err)
	}

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

		if err := validateUsername(username); err != nil {
			return c.Status(http.StatusBadRequest).SendString(err.Error())
		}

		profilePhoto, err := readFile(profilePhotoFile)
		if err != nil || !isValidPNG(profilePhotoFile) {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}

		profilePage = sanitizeHTML(profilePage)

		_, err = db.Exec("INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)", username, profilePage, profilePhoto)
		if err != nil {
			if err.Error() == "UNIQUE constraint failed: profiles.username" {
				return c.Status(http.StatusForbidden).SendString("Profile already exists, creation forbidden")
			}
			return c.Status(http.StatusInternalServerError).SendString("Error creating profile")
		}

		return c.Status(http.StatusCreated).SendString("Profile created successfully")
	})

	app.Get("/profile/:username", func(c *fiber.Ctx) error {
		username := c.Params("username")
		var profile Profile
		err := db.QueryRow("SELECT profile_page FROM profiles WHERE username = ?", username).Scan(&profile.ProfilePage)
		if err != nil {
			if err == sql.ErrNoRows {
				return c.Status(http.StatusNotFound).SendString("Profile not found")
			}
			return c.Status(http.StatusInternalServerError).SendString("Error retrieving profile")
		}
		return c.SendString(profile.ProfilePage)
	})

	app.Get("/profile-photo/:username", func(c *fiber.Ctx) error {
		username := c.Params("username")
		var profile Profile
		err := db.QueryRow("SELECT profile_photo FROM profiles WHERE username = ?", username).Scan(&profile.ProfilePhoto)
		if err != nil {
			if err == sql.ErrNoRows {
				return c.Status(http.StatusNotFound).SendString("Profile photo not found")
			}
			return c.Status(http.StatusInternalServerError).SendString("Error retrieving profile photo")
		}
		return c.Send(profile.ProfilePhoto)
	})

	app.Listen(":5000")
}

func readFile(fileHeader *multipart.FileHeader) ([]byte, error) {
	file, err := fileHeader.Open()
	if err != nil {
		return nil, err
	}
	defer file.Close()
	return ioutil.ReadAll(file)
}

func isValidPNG(fileHeader *multipart.FileHeader) bool {
	return fileHeader.Header.Get("Content-Type") == "image/png"
}

func validateUsername(username string) error {
	if len(username) < 3 || len(username) > 20 {
		return fmt.Errorf("Invalid username")
	}
	if matched, _ := regexp.MatchString("^[a-zA-Z0-9_]+$", username); !matched {
		return fmt.Errorf("Username can only contain alphanumeric characters and underscores")
	}
	return nil
}

func sanitizeHTML(html string) string {
	return template.HTMLEscapeString(html)
}