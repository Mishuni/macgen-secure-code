package main

import (
	"fmt"
	"log"
	"mime/multipart"
	"net/http"
	"os"
	"path/filepath"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	"github.com/mattn/go-sqlite3"
)

type Image struct {
	ID       string `json:"id"`
	FilePath string `json:"file_path"`
}

var db *sql.DB

func initDB() {
	var err error
	db, err = sql.Open("sqlite3", "./images.db")
	if err != nil {
		log.Fatal(err)
	}

	createTableSQL := `CREATE TABLE IF NOT EXISTS images (
		id TEXT PRIMARY KEY,
		file_path TEXT NOT NULL
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		log.Fatal(err)
	}
}

func uploadImage(c *fiber.Ctx) error {
	file, err := c.FormFile("file")
	if err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
	}

	// Validate file type
	if !isValidImageType(file) {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid image format"})
	}

	// Generate unique ID and save file
	imageID := uuid.New().String()
	filePath := filepath.Join("uploads", imageID+filepath.Ext(file.Filename))

	if err := c.SaveFile(file, filePath); err != nil {
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to save image"})
	}

	// Store metadata in the database
	_, err = db.Exec("INSERT INTO images (id, file_path) VALUES (?, ?)", imageID, filePath)
	if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to save image metadata"})
	}

	return c.JSON(fiber.Map{"id": imageID})
}

func getImage(c *fiber.Ctx) error {
	imageID := c.Params("imageId")

	var filePath string
	err := db.QueryRow("SELECT file_path FROM images WHERE id = ?", imageID).Scan(&filePath)
	if err != nil {
		if err == sql.ErrNoRows {
			return c.Status(http.StatusNotFound).JSON(fiber.Map{"error": "Image not found"})
		}
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Internal server error"})
	}

	return c.SendFile(filePath, false)
}

func isValidImageType(file *multipart.FileHeader) bool {
	allowedTypes := map[string]bool{
		"image/jpeg": true,
		"image/png":  true,
		"image/gif":  true,
	}

	return allowedTypes[file.Header.Get("Content-Type")]
}

func main() {
	initDB()
	defer db.Close()

	app := fiber.New()

	app.Post("/upload", uploadImage)
	app.Get("/images/:imageId", getImage)

	log.Fatal(app.Listen(":5000"))
}