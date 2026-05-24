package main

import (
	"database/sql"
	"fmt"
	"log"
	"mime/multipart"
	"net/http"
	"os"

	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/logger"
	"github.com/gofiber/fiber/v2/middleware/recover"
	"github.com/h2non/filetype"
	"github.com/microcosm-cc/bluemonday"
	_ "github.com/mattn/go-sqlite3"
)

func main() {
	app := fiber.New()

	// Middleware
	app.Use(logger.New())
	app.Use(recover.New())

	// Initialize SQLite database
	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to open database: %v", err)
	}
	defer db.Close()

	// Create profiles table if it doesn't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS profiles (
		username TEXT PRIMARY KEY,
		profile_page TEXT,
		profile_photo BLOB
	)`)
	if err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}

	// Route to add a new profile
	app.Post("/add_profile", func(c *fiber.Ctx) error {
		username := c.FormValue("username")
		profilePage := c.FormValue("profile_page")
		profilePhoto, err := c.FormFile("profile_photo")
		if err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid input")
		}

		// Validate file size (e.g., max 5MB)
		if profilePhoto.Size > 5*1024*1024 {
			return c.Status(fiber.StatusBadRequest).SendString("File too large")
		}

		// Check if profile already exists
		var exists bool
		err = db.QueryRow("SELECT EXISTS(SELECT 1 FROM profiles WHERE username=?)", username).Scan(&exists)
		if err != nil {
			log.Printf("Database error: %v", err)
			return c.Status(fiber.StatusInternalServerError).SendString("Internal server error")
		}
		if exists {
			return c.Status(fiber.StatusForbidden).SendString("Profile already exists")
		}

		// Read and validate profile photo
		file, err := profilePhoto.Open()
		if err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid input")
		}
		defer file.Close()

		photoData := make([]byte, profilePhoto.Size)
		_, err = file.Read(photoData)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Error reading file")
		}

		// Validate file type
		if !isValidImage(photoData) {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid file type")
		}

		// Insert new profile
		_, err = db.Exec("INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)", username, sanitizeHTML(profilePage), photoData)
		if err != nil {
			log.Printf("Database error: %v", err)
			return c.Status(fiber.StatusInternalServerError).SendString("Internal server error")
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
			log.Printf("Database error: %v", err)
			return c.Status(fiber.StatusInternalServerError).SendString("Internal server error")
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
			log.Printf("Database error: %v", err)
			return c.Status(fiber.StatusInternalServerError).SendString("Internal server error")
		}

		// Determine the MIME type dynamically
		kind, err := filetype.Match(profilePhoto)
		if err != nil || kind == filetype.Unknown {
			return c.Status(fiber.StatusInternalServerError).SendString("Error determining file type")
		}

		return c.Type(kind.MIME.Value).Send(profilePhoto)
	})

	log.Fatal(app.Listen("0.0.0.0:5000"))
}

// isValidImage checks if the file is a valid image type
func isValidImage(data []byte) bool {
	kind, err := filetype.Match(data)
	if err != nil {
		return false
	}
	return kind.MIME.Type == "image" && (kind.Extension == "jpeg" || kind.Extension == "png")
}

// sanitizeHTML removes potentially harmful HTML tags
func sanitizeHTML(input string) string {
	p := bluemonday.UGCPolicy()
	return p.Sanitize(input)
}