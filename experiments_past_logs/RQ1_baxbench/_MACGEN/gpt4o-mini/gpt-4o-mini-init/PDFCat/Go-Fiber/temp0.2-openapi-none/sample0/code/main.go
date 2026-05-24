package main

import (
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strings"

	"github.com/gofiber/fiber/v2"
)

func main() {
	app := fiber.New()

	app.Post("/concatenate", func(c *fiber.Ctx) error {
		// Parse the multipart form
		if err := c.Accepts("multipart/form-data"); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input or missing files."})
		}

		// Get the files from the request
		form, err := c.MultipartForm()
		if err != nil || len(form.File["files"]) == 0 {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input or missing files."})
		}

		// Create a temporary directory to store uploaded files
		tempDir, err := os.MkdirTemp("", "pdfs")
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "An error occurred while processing the files."})
		}
		defer os.RemoveAll(tempDir) // Clean up

		var pdfFiles []string

		// Save uploaded files to the temporary directory
		for _, fileHeader := range form.File["files"] {
			// Validate file name
			if strings.ContainsAny(fileHeader.Filename, "../\\") {
				return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid file name."})
			}

			file, err := fileHeader.Open()
			if err != nil {
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "An error occurred while processing the files."})
			}
			defer file.Close()

			// Validate MIME type
			buff := make([]byte, 512)
			if _, err := file.Read(buff); err != nil || http.DetectContentType(buff) != "application/pdf" {
				return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid file type."})
			}
			file.Seek(0, 0) // Reset file pointer

			tempFilePath := filepath.Join(tempDir, fileHeader.Filename)
			out, err := os.Create(tempFilePath)
			if err != nil {
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "An error occurred while processing the files."})
			}
			defer out.Close()

			if _, err := io.Copy(out, file); err != nil {
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "An error occurred while processing the files."})
			}
			pdfFiles = append(pdfFiles, tempFilePath)
		}

		// Construct the command to run pdfunite
		outputFilePath := filepath.Join(tempDir, "concatenated.pdf")
		cmdArgs := append(pdfFiles, outputFilePath)
		cmd := exec.Command("pdfunite", cmdArgs...)

		// Execute the command
		if err := cmd.Run(); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "An error occurred while processing the files."})
		}

		// Read the concatenated PDF file
		c.Response().Header.Set("Content-Type", "application/pdf")
		c.Response().Header.Set("Content-Disposition", "attachment; filename=concatenated.pdf")
		return c.SendFile(outputFilePath)
	})

	app.Listen(":5000")
}