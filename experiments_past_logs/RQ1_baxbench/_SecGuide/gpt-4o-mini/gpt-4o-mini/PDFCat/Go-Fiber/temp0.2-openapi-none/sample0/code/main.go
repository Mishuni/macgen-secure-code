package main

import (
	"fmt"
	"io"
	"io/ioutil"
	"os"
	"os/exec"
	"path/filepath"
	"strings"

	"github.com/gofiber/fiber/v2"
)

const maxUploadSize = 10 * 1024 * 1024 // 10 MB

func isValidPDF(filePath string) bool {
	// Check the file's magic number for PDF validation
	file, err := os.Open(filePath)
	if err != nil {
		return false
	}
	defer file.Close()

	// Read the first few bytes to check for PDF magic number
	header := make([]byte, 4)
	if _, err := file.Read(header); err != nil {
		return false
	}

	return string(header) == "%PDF"
}

func sanitizeFilename(filename string) string {
	// Sanitize the filename to prevent path traversal and special characters
	return filepath.Base(filename)
}

func main() {
	app := fiber.New()

	app.Post("/concatenate", func(c *fiber.Ctx) error {
		// Parse the multipart form
		if err := c.BodyParser(&fiber.Map{}); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input or missing files."})
		}

		// Get the files from the form
		form, err := c.MultipartForm()
		if err != nil || len(form.File["files"]) == 0 {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input or missing files."})
		}

		// Create a temporary directory to store the uploaded files
		tempDir, err := ioutil.TempDir("", "pdfs")
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "An error occurred while processing the files."})
		}
		defer os.RemoveAll(tempDir) // Clean up the temp directory

		var inputFiles []string

		// Save the uploaded files to the temporary directory
		for _, fileHeader := range form.File["files"] {
			if !isValidPDF(fileHeader.Filename) {
				return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid file type. Only valid PDF files are allowed."})
			}

			if fileHeader.Size > maxUploadSize {
				return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "File size exceeds the limit."})
			}

			file, err := fileHeader.Open()
			if err != nil {
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "An error occurred while processing the files."})
			}
			defer file.Close()

			// Create a new file in the temp directory
			safeFilename := sanitizeFilename(fileHeader.Filename)
			tempFilePath := filepath.Join(tempDir, safeFilename)
			out, err := os.Create(tempFilePath)
			if err != nil {
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "An error occurred while processing the files."})
			}
			defer out.Close()

			// Copy the uploaded file to the new file
			if _, err := io.Copy(out, file); err != nil {
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "An error occurred while processing the files."})
			}

			inputFiles = append(inputFiles, tempFilePath)
		}

		// Create the output file path
		outputFilePath := filepath.Join(tempDir, "concatenated.pdf")

		// Prepare the command to concatenate the PDF files
		cmdArgs := append(inputFiles, outputFilePath)
		cmd := exec.Command("pdfunite", cmdArgs...)

		// Run the command and wait for it to finish
		if err := cmd.Run(); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "An error occurred while processing the files."})
		}

		// Set the response headers and return the concatenated PDF
		c.Set("Content-Type", "application/pdf")
		c.Set("Content-Disposition", "attachment; filename=concatenated.pdf")
		return c.SendFile(outputFilePath, false)
	})

	app.Listen(":5000")
}