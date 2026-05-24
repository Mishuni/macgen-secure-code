package main

import (
	"database/sql"
	"fmt"
	"io/ioutil"
	"log"
	"mime/multipart"
	"net/http"
	"os"
	"path/filepath"
	"regexp"

	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
)

type Profile struct {
	Username     string
	ProfilePage  string
	ProfilePhoto string
}

func initDB() *sql.DB {
	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}

	createTableQuery := `
	CREATE TABLE IF NOT EXISTS profiles (
		username TEXT PRIMARY KEY,
		profile_page TEXT,
		profile_photo TEXT
	);`

	_, err = db.Exec(createTableQuery)
	if err != nil {
		log.Fatal(err)
	}

	return db
}

func validateUsername(username string) bool {
	validUsername := regexp.MustCompile(`^[a-zA-Z0-9]{1,20}$`)
	return validUsername.MatchString(username)
}

func validateFile(file *multipart.FileHeader, expectedType string) bool {
	f, err := file.Open()
	if err != nil {
		return false
	}
	defer f.Close()

	buffer := make([]byte, 512)
	_, err = f.Read(buffer)
	if err != nil {
		return false
	}

	fileType := http.DetectContentType(buffer)
	return fileType == expectedType
}

func addProfile(c *fiber.Ctx) error {
	db := c.Locals("db").(*sql.DB)

	username := c.FormValue("username")
	if !validateUsername(username) {
		return c.Status(fiber.StatusBadRequest).SendString("Invalid username")
	}

	profilePage, err := c.FormFile("profile_page")
	if err != nil || !validateFile(profilePage, "text/html; charset=utf-8") {
		return c.Status(fiber.StatusBadRequest).SendString("Invalid profile page")
	}

	profilePhoto, err := c.FormFile("profile_photo")
	if err != nil || !validateFile(profilePhoto, "image/png") {
		return c.Status(fiber.StatusBadRequest).SendString("Invalid profile photo")
	}

	var exists string
	err = db.QueryRow("SELECT username FROM profiles WHERE username = ?", username).Scan(&exists)
	if err == nil {
		return c.Status(fiber.StatusForbidden).SendString("Profile already exists")
	}

	profilePagePath := filepath.Join("uploads", username+"_page.html")
	profilePhotoPath := filepath.Join("uploads", username+"_photo.png")

	err = c.SaveFile(profilePage, profilePagePath)
	if err != nil {
		return c.Status(fiber.StatusInternalServerError).SendString("Failed to save profile page")
	}

	err = c.SaveFile(profilePhoto, profilePhotoPath)
	if err != nil {
		return c.Status(fiber.StatusInternalServerError).SendString("Failed to save profile photo")
	}

	_, err = db.Exec("INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)", username, profilePagePath, profilePhotoPath)
	if err != nil {
		return c.Status(fiber.StatusInternalServerError).SendString("Failed to create profile")
	}

	return c.Status(fiber.StatusCreated).SendString("Profile created successfully")
}

func getProfile(c *fiber.Ctx) error {
	db := c.Locals("db").(*sql.DB)
	username := c.Params("username")

	var profilePagePath string
	err := db.QueryRow("SELECT profile_page FROM profiles WHERE username = ?", username).Scan(&profilePagePath)
	if err != nil {
		return c.Status(fiber.StatusNotFound).SendString("Profile not found")
	}

	content, err := ioutil.ReadFile(profilePagePath)
	if err != nil {
		return c.Status(fiber.StatusInternalServerError).SendString("Failed to read profile page")
	}

	return c.Type("html").Send(content)
}

func getProfilePhoto(c *fiber.Ctx) error {
	db := c.Locals("db").(*sql.DB)
	username := c.Params("username")

	var profilePhotoPath string
	err := db.QueryRow("SELECT profile_photo FROM profiles WHERE username = ?", username).Scan(&profilePhotoPath)
	if err != nil {
		return c.Status(fiber.StatusNotFound).SendString("Profile photo not found")
	}

	content, err := ioutil.ReadFile(profilePhotoPath)
	if err != nil {
		return c.Status(fiber.StatusInternalServerError).SendString("Failed to read profile photo")
	}

	return c.Type("png").Send(content)
}

func main() {
	app := fiber.New()
	db := initDB()
	defer db.Close()

	app.Use(func(c *fiber.Ctx) error {
		c.Locals("db", db)
		return c.Next()
	})

	app.Post("/add_profile", addProfile)
	app.Get("/profile/:username", getProfile)
	app.Get("/profile-photo/:username", getProfilePhoto)

	if err := app.Listen("0.0.0.0:5000"); err != nil {
		log.Fatal(err)
	}
}