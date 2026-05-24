package main

import (
	"database/sql"
	"fmt"
	"html/template"
	"log"
	"net/http"
	"os"
	"strings"

	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
)

const (
	dbFileName = "db.sqlite3"
)

func initDB() (*sql.DB, error) {
	db, err := sql.Open("sqlite3", dbFileName)
	if err != nil {
		return nil, err
	}

	createTableQuery := `
	CREATE TABLE IF NOT EXISTS profiles (
		username TEXT PRIMARY KEY,
		profile_page TEXT,
		profile_photo BLOB
	);`
	_, err = db.Exec(createTableQuery)
	if err != nil {
		return nil, err
	}

	return db, nil
}

func main() {
	app := fiber.New()

	db, err := initDB()
	if err != nil {
		log.Fatalf("Failed to initialize database: %v", err)
	}
	defer db.Close()

	app.Post("/add_profile", func(c *fiber.Ctx) error {
		username := c.FormValue("username")
		profilePage := c.FormValue("profile_page")
		profilePhoto, err := c.FormFile("profile_photo")

		if err != nil || username == "" || profilePage == "" || profilePhoto == nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}

		// Check if profile already exists
		var exists bool
		err = db.QueryRow("SELECT EXISTS(SELECT 1 FROM profiles WHERE username=?)", username).Scan(&exists)
		if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Database error")
		}
		if exists {
			return c.Status(http.StatusForbidden).SendString("Profile already exists")
		}

		// Read profile photo
		file, err := profilePhoto.Open()
		if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Failed to read profile photo")
		}
		defer file.Close()

		photoData := make([]byte, profilePhoto.Size)
		_, err = file.Read(photoData)
		if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Failed to read profile photo")
		}

		// Insert profile into database
		_, err = db.Exec("INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)", username, profilePage, photoData)
		if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Failed to create profile")
		}

		return c.Status(http.StatusCreated).SendString("Profile created successfully")
	})

	app.Get("/profile/:username", func(c *fiber.Ctx) error {
		username := c.Params("username")

		var profilePage string
		err := db.QueryRow("SELECT profile_page FROM profiles WHERE username=?", username).Scan(&profilePage)
		if err == sql.ErrNoRows {
			return c.Status(http.StatusNotFound).SendString("Profile not found")
		} else if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Database error")
		}

		// Escape HTML content to prevent XSS
		escapedProfilePage := template.HTMLEscapeString(profilePage)
		return c.Type("text/html").SendString(escapedProfilePage)
	})

	app.Get("/profile-photo/:username", func(c *fiber.Ctx) error {
		username := c.Params("username")

		var profilePhoto []byte
		err := db.QueryRow("SELECT profile_photo FROM profiles WHERE username=?", username).Scan(&profilePhoto)
		if err == sql.ErrNoRows {
			return c.Status(http.StatusNotFound).SendString("Profile photo not found")
		} else if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Database error")
		}

		return c.Type("image/png").Send(profilePhoto)
	})

	log.Fatal(app.Listen("0.0.0.0:5000"))
}