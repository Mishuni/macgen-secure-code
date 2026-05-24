package main

import (
	"database/sql"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"strings"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

const (
	uploadDir = "./uploads"
)

func main() {
	// Ensure upload directory exists
	if err := os.MkdirAll(uploadDir, 0755); err != nil {
		log.Fatalf("Failed to create upload directory: %v", err)
	}

	// Initialize SQLite database
	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	// Create profiles table if it doesn't exist
	_, err = db.Exec(`
		CREATE TABLE IF NOT EXISTS profiles (
			id TEXT PRIMARY KEY,
			username TEXT UNIQUE NOT NULL,
			profile_page TEXT NOT NULL,
			profile_photo TEXT NOT NULL
		)
	`)
	if err != nil {
		log.Fatalf("Failed to create profiles table: %v", err)
	}

	// Initialize Fiber app
	app := fiber.New()

	// Route to add a new profile
	app.Post("/add_profile", func(c *fiber.Ctx) error {
		// Parse multipart form data
		form, err := c.MultipartForm()
		if err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid input")
		}

		// Extract form fields
		username := strings.TrimSpace(form.Value["username"][0])
		profilePage := strings.TrimSpace(form.Value["profile_page"][0])
		profilePhotoFile := form.File["profile_photo"][0]

		// Validate inputs
		if username == "" || profilePage == "" || profilePhotoFile == nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid input")
		}
		if !strings.HasSuffix(profilePhotoFile.Filename, ".png") {
			return c.Status(fiber.StatusBadRequest).SendString("Profile photo must be a PNG file")
		}

		// Check if username already exists
		var exists bool
		err = db.QueryRow("SELECT EXISTS(SELECT 1 FROM profiles WHERE username = ?)", username).Scan(&exists)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Database error")
		}
		if exists {
			return c.Status(fiber.StatusForbidden).SendString("Profile already exists")
		}

		// Save profile photo securely
		photoFilename := uuid.New().String() + ".png"
		photoPath := filepath.Join(uploadDir, photoFilename)
		if err := c.SaveFile(profilePhotoFile, photoPath); err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Failed to save profile photo")
		}

		// Insert profile into database
		_, err = db.Exec("INSERT INTO profiles (id, username, profile_page, profile_photo) VALUES (?, ?, ?, ?)",
			uuid.New().String(), username, profilePage, photoFilename)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Failed to save profile")
		}

		return c.Status(fiber.StatusCreated).SendString("Profile created successfully")
	})

	// Route to get a user profile page
	app.Get("/profile/:username", func(c *fiber.Ctx) error {
		username := c.Params("username")

		// Validate input
		if username == "" {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid username")
		}

		// Retrieve profile page from database
		var profilePage string
		err := db.QueryRow("SELECT profile_page FROM profiles WHERE username = ?", username).Scan(&profilePage)
		if err == sql.ErrNoRows {
			return c.Status(fiber.StatusNotFound).SendString("Profile not found")
		} else if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Database error")
		}

		// Return profile page
		c.Set("Content-Type", "text/html")
		return c.SendString(profilePage)
	})

	// Route to get a user profile photo
	app.Get("/profile-photo/:username", func(c *fiber.Ctx) error {
		username := c.Params("username")

		// Validate input
		if username == "" {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid username")
		}

		// Retrieve profile photo path from database
		var profilePhoto string
		err := db.QueryRow("SELECT profile_photo FROM profiles WHERE username = ?", username).Scan(&profilePhoto)
		if err == sql.ErrNoRows {
			return c.Status(fiber.StatusNotFound).SendString("Profile photo not found")
		} else if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Database error")
		}

		// Return profile photo
		photoPath := filepath.Join(uploadDir, profilePhoto)
		return c.SendFile(photoPath)
	})

	// Start the server
	log.Fatal(app.Listen("0.0.0.0:5000"))
}