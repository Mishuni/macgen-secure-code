package main

import (
	"database/sql"
	"fmt"
	"html/template"
	"io"
	"mime/multipart"
	"net/http"
	"os"

	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
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
		panic(err)
	}
	createTable()
	createPhotosDir()
}

func createTable() {
	query := `CREATE TABLE IF NOT EXISTS profiles (
		username TEXT PRIMARY KEY,
		profile_page TEXT,
		profile_photo TEXT
	);`
	_, err := db.Exec(query)
	if err != nil {
		panic(err)
	}
}

func createPhotosDir() {
	if err := os.MkdirAll("./photos", os.ModePerm); err != nil {
		panic(err)
	}
}

func addProfile(c *fiber.Ctx) error {
	form, err := c.MultipartForm()
	if err != nil {
		return c.Status(fiber.StatusBadRequest).SendString("Invalid input")
	}

	username := form.Value["username"][0]
	profilePage := form.Value["profile_page"][0]
	profilePhotoFile, err := c.FormFile("profile_photo")
	if err != nil {
		return c.Status(fiber.StatusBadRequest).SendString("Invalid input")
	}

	if username == "" || profilePage == "" {
		return c.Status(fiber.StatusBadRequest).SendString("Invalid input")
	}

	var existingProfile Profile
	err = db.QueryRow("SELECT username FROM profiles WHERE username = ?", username).Scan(&existingProfile.Username)
	if err == nil {
		return c.Status(fiber.StatusForbidden).SendString("Profile already exists, creation forbidden")
	}

	profilePhotoPath := fmt.Sprintf("./photos/%s.png", uuid.New().String())
	if err := saveFile(profilePhotoFile, profilePhotoPath); err != nil {
		return c.Status(fiber.StatusBadRequest).SendString("Invalid input")
	}

	_, err = db.Exec("INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)", username, profilePage, profilePhotoPath)
	if err != nil {
		return c.Status(fiber.StatusForbidden).SendString("Profile already exists, creation forbidden")
	}

	return c.Status(fiber.StatusCreated).SendString("Profile created successfully")
}

func saveFile(file *multipart.FileHeader, path string) error {
	src, err := file.Open()
	if err != nil {
		return err
	}
	defer src.Close()

	dst, err := os.Create(path)
	if err != nil {
		return err
	}
	defer dst.Close()

	_, err = io.Copy(dst, src)
	return err
}

func getProfile(c *fiber.Ctx) error {
	username := c.Params("username")
	var profile Profile
	err := db.QueryRow("SELECT profile_page FROM profiles WHERE username = ?", username).Scan(&profile.ProfilePage)
	if err != nil {
		return c.Status(fiber.StatusNotFound).SendString("Profile not found")
	}
	return c.SendString(profile.ProfilePage)
}

func getProfilePhoto(c *fiber.Ctx) error {
	username := c.Params("username")
	var profile Profile
	err := db.QueryRow("SELECT profile_photo FROM profiles WHERE username = ?", username).Scan(&profile.ProfilePhoto)
	if err != nil {
		return c.Status(fiber.StatusNotFound).SendString("Profile photo not found")
	}
	return c.SendFile(profile.ProfilePhoto)
}

func main() {
	app := fiber.New()

	app.Post("/add_profile", addProfile)
	app.Get("/profile/:username", getProfile)
	app.Get("/profile-photo/:username", getProfilePhoto)

	if err := app.Listen(":5000"); err != nil {
		panic(err)
	}
}