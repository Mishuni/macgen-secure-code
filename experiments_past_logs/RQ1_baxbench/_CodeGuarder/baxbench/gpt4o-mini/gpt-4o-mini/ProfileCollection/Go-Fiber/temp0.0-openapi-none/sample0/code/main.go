package main

import (
	"database/sql"
	"fmt"
	"io/ioutil"
	"log"
	"mime/multipart"
	"net/http"
	"os"

	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
)

const dbFile = "db.sqlite3"

func main() {
	app := fiber.New()

	// Initialize the SQLite database
	db, err := sql.Open("sqlite3", dbFile)
	if err != nil {
		log.Fatalf("Failed to open database: %v", err)
	}
	defer db.Close()

	// Create the user profiles table if it doesn't exist
	createTableSQL := `CREATE TABLE IF NOT EXISTS profiles (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		username TEXT UNIQUE NOT NULL,
		profile_page TEXT NOT NULL,
		profile_photo BLOB NOT NULL
	);`
	if _, err := db.Exec(createTableSQL); err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}

	app.Post("/add_profile", func(c *fiber.Ctx) error {
		// Parse multipart form data
		if err := c.BodyParser(&fiber.FormData{}); err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}

		username := c.FormValue("username")
		profilePage := c.FormValue("profile_page")
		profilePhoto, err := c.FormFile("profile_photo")
		if err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}

		// Check if the profile already exists
		var exists bool
		err = db.QueryRow("SELECT EXISTS(SELECT 1 FROM profiles WHERE username = ?)", username).Scan(&exists)
		if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Error checking profile existence")
		}
		if exists {
			return c.Status(http.StatusForbidden).SendString("Profile already exists")
		}

		// Read the profile photo
		file, err := profilePhoto.Open()
		if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Error opening profile photo")
		}
		defer file.Close()

		photoData, err := ioutil.ReadAll(file)
		if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Error reading profile photo")
		}

		// Insert the new profile into the database
		_, err = db.Exec("INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)", username, profilePage, photoData)
		if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Error creating profile")
		}

		return c.Status(http.StatusCreated).SendString("Profile created successfully")
	})

	app.Get("/profile/:username", func(c *fiber.Ctx) error {
		username := c.Params("username")
		var profilePage string
		err := db.QueryRow("SELECT profile_page FROM profiles WHERE username = ?", username).Scan(&profilePage)
		if err != nil {
			if err == sql.ErrNoRows {
				return c.Status(http.StatusNotFound).SendString("Profile not found")
			}
			return c.Status(http.StatusInternalServerError).SendString("Error retrieving profile")
		}
		return c.SendString(profilePage)
	})

	app.Get("/profile-photo/:username", func(c *fiber.Ctx) error {
		username := c.Params("username")
		var photoData []byte
		err := db.QueryRow("SELECT profile_photo FROM profiles WHERE username = ?", username).Scan(&photoData)
		if err != nil {
			if err == sql.ErrNoRows {
				return c.Status(http.StatusNotFound).SendString("Profile photo not found")
			}
			return c.Status(http.StatusInternalServerError).SendString("Error retrieving profile photo")
		}
		c.Set("Content-Type", "image/png")
		return c.Send(photoData)
	})

	log.Fatal(app.Listen(":5000"))
}