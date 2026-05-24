package main

import (
	"database/sql"
	"fmt"
	"log"
	"mime/multipart"
	"os"
	"strings"

	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
)

func main() {
	app := fiber.New()

	// Initialize SQLite database
	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Create profiles table if not exists
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS profiles (
		username TEXT PRIMARY KEY,
		profile_page TEXT,
		profile_photo BLOB
	)`)
	if err != nil {
		log.Fatal(err)
	}

	// Route to add a new profile
	app.Post("/add_profile", func(c *fiber.Ctx) error {
		username := c.FormValue("username")
		profilePage := c.FormValue("profile_page")
		profilePhoto, err := c.FormFile("profile_photo")
		if err != nil || !isValidPNG(profilePhoto) {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid input")
		}

		// Check if profile already exists
		var exists bool
		err = db.QueryRow("SELECT EXISTS(SELECT 1 FROM profiles WHERE username=?)", username).Scan(&exists)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Database error")
		}
		if exists {
			return c.Status(fiber.StatusForbidden).SendString("Profile already exists, creation forbidden")
		}

		// Read profile photo
		file, err := profilePhoto.Open()
		if err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid input")
		}
		defer file.Close()

		photoData := make([]byte, profilePhoto.Size)
		_, err = file.Read(photoData)
		if err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid input")
		}

		// Insert new profile
		_, err = db.Exec("INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)", username, profilePage, photoData)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Database error")
		}

		return c.Status(fiber.StatusCreated).SendString("Profile created successfully")
	})

	// Route to get a user profile
	app.Get("/profile/:username", func(c *fiber.Ctx) error {
		username := c.Params("username")

		var profilePage string
		err := db.QueryRow("SELECT profile_page FROM profiles WHERE username=?", username).Scan(&profilePage)
		if err == sql.ErrNoRows {
			return c.Status(fiber.StatusNotFound).SendString("Profile not found")
		} else if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Database error")
		}

		return c.Type("text/html").SendString(profilePage)
	})

	// Route to get a user profile photo
	app.Get("/profile-photo/:username", func(c *fiber.Ctx) error {
		username := c.Params("username")

		var profilePhoto []byte
		err := db.QueryRow("SELECT profile_photo FROM profiles WHERE username=?", username).Scan(&profilePhoto)
		if err == sql.ErrNoRows {
			return c.Status(fiber.StatusNotFound).SendString("Profile photo not found")
		} else if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Database error")
		}

		return c.Type("image/png").Send(profilePhoto)
	})

	// Start server
	log.Fatal(app.Listen("0.0.0.0:5000"))
}

// isValidPNG checks if the uploaded file is a valid PNG image
func isValidPNG(fileHeader *multipart.FileHeader) bool {
	return strings.HasSuffix(fileHeader.Filename, ".png")
}