package main

import (
	"database/sql"
	"fmt"
	"log"
	"mime/multipart"
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

const (
	uploadDir = "./uploads"
	dbFile    = "./images.db"
)

func main() {
	// Initialize the Fiber app
	app := fiber.New()

	// Ensure the upload directory exists
	if err := os.MkdirAll(uploadDir, 0755); err != nil {
		log.Fatalf("Failed to create upload directory: %v", err)
	}

	// Initialize the SQLite database
	db, err := sql.Open("sqlite3", dbFile)
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	// Create the images table if it doesn't exist
	if _, err := db.Exec(`CREATE TABLE IF NOT EXISTS images (id TEXT PRIMARY KEY, filename TEXT NOT NULL)`); err != nil {
		log.Fatalf("Failed to create images table: %v", err)
	}

	// Route to handle image uploads
	app.Post("/upload", func(c *fiber.Ctx) error {
		// Parse the multipart form
		form, err := c.MultipartForm()
		if err != nil {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid form data"})
		}

		// Get the file from the form
		files := form.File["file"]
		if len(files) == 0 {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "No file provided"})
		}

		file := files[0]
		if err := validateFile(file); err != nil {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": err.Error()})
		}

		// Generate a unique ID for the image
		imageID := uuid.New().String()
		filePath := filepath.Join(uploadDir, imageID+filepath.Ext(file.Filename))

		// Save the file to the upload directory
		if err := c.SaveFile(file, filePath); err != nil {
			return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to save file"})
		}

		// Store the image metadata in the database
		if _, err := db.Exec("INSERT INTO images (id, filename) VALUES (?, ?)", imageID, filepath.Base(filePath)); err != nil {
			return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to save metadata"})
		}

		// Return the shareable link
		return c.Status(http.StatusOK).JSON(fiber.Map{"id": imageID})
	})

	// Route to handle image sharing
	app.Get("/images/:imageId", func(c *fiber.Ctx) error {
		imageID := c.Params("imageId")

		// Retrieve the image metadata from the database
		var filename string
		if err := db.QueryRow("SELECT filename FROM images WHERE id = ?", imageID).Scan(&filename); err != nil {
			if err == sql.ErrNoRows {
				return c.Status(http.StatusNotFound).JSON(fiber.Map{"error": "Image not found"})
			}
			return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to retrieve image metadata"})
		}

		// Construct the full file path
		filePath := filepath.Join(uploadDir, filename)

		// Serve the image file
		return c.SendFile(filePath, false)
	})

	// Start the server
	log.Fatal(app.Listen("0.0.0.0:5000"))
}

// validateFile ensures the uploaded file is a valid image
func validateFile(file *multipart.FileHeader) error {
	// Check the file extension
	ext := strings.ToLower(filepath.Ext(file.Filename))
	if ext != ".jpg" && ext != ".jpeg" && ext != ".png" && ext != ".gif" {
		return fmt.Errorf("unsupported file format")
	}

	// Check the file size (e.g., limit to 10MB)
	const maxFileSize = 10 * 1024 * 1024 // 10MB
	if file.Size > maxFileSize {
		return fmt.Errorf("file size exceeds the 10MB limit")
	}

	return nil
}