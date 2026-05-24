package main

import (
	"fmt"
	"html/template"
	"io/ioutil"
	"mime/multipart"
	"net/http"
	"os"

	"github.com/gofiber/fiber/v2"
	"github.com/mattn/go-sqlite3"
)

type Profile struct {
	Username     string
	ProfilePage  string
	ProfilePhoto string
}

func main() {
	app := fiber.New()

	// Initialize the SQLite database
	db, err := sqlite3.Open("db.sqlite3")
	if err != nil {
		fmt.Println("Error opening database:", err)
		return
	}
	defer db.Close()

	// Create the profiles table if it doesn't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS profiles (
		username TEXT PRIMARY KEY,
		profile_page TEXT,
		profile_photo TEXT
	)`)
	if err != nil {
		fmt.Println("Error creating table:", err)
		return
	}

	app.Post("/add_profile", func(c *fiber.Ctx) error {
		// Parse the multipart form
		err := c.BodyParser(&Profile{})
		if err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}

		username := c.FormValue("username")
		profilePage := c.FormValue("profile_page")
		profilePhoto := c.FormValue("profile_photo")

		// Check if the profile already exists
		var existingProfile Profile
		err = db.QueryRow("SELECT * FROM profiles WHERE username = ?", username).Scan(&existingProfile.Username, &existingProfile.ProfilePage, &existingProfile.ProfilePhoto)
		if err == nil {
			return c.Status(http.StatusForbidden).SendString("Profile already exists, creation forbidden")
		}

		// Insert the new profile into the database
		_, err = db.Exec("INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)", username, profilePage, profilePhoto)
		if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Error creating profile")
		}

		return c.Status(http.StatusCreated).SendString("Profile created successfully")
	})

	app.Get("/profile/:username", func(c *fiber.Ctx) error {
		username := c.Params("username")

		var profile Profile
		err := db.QueryRow("SELECT * FROM profiles WHERE username = ?", username).Scan(&profile.Username, &profile.ProfilePage, &profile.ProfilePhoto)
		if err != nil {
			return c.Status(http.StatusNotFound).SendString("Profile not found")
		}

		return c.SendString(profile.ProfilePage)
	})

	app.Get("/profile-photo/:username", func(c *fiber.Ctx) error {
		username := c.Params("username")

		var profile Profile
		err := db.QueryRow("SELECT * FROM profiles WHERE username = ?", username).Scan(&profile.Username, &profile.ProfilePage, &profile.ProfilePhoto)
		if err != nil {
			return c.Status(http.StatusNotFound).SendString("Profile photo not found")
		}

		// Serve the profile photo
		return c.SendFile(profile.ProfilePhoto)
	})

	app.Listen(":5000")
}