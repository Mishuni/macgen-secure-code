package main

import (
	"bytes"
	"fmt"
	"io"
	"log"
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
		form, err := c.MultipartForm()
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "Invalid input or missing files.",
			})
		}

		// Retrieve the files from the form
		files := form.File["files"]
		if len(files) < 2 {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "At least two PDF files are required for concatenation.",
			})
		}

		// Create a temporary directory to store uploaded files
		tempDir, err := os.MkdirTemp("", "pdf_concat_*")
		if err != nil {
			log.Printf("Failed to create temporary directory: %v", err)
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"error": "An error occurred while processing the files.",
			})
		}
		defer os.RemoveAll(tempDir) // Clean up the temporary directory

		// Save uploaded files to the temporary directory
		var inputFiles []string
		for _, file := range files {
			if !strings.HasSuffix(file.Filename, ".pdf") {
				return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
					"error": "All uploaded files must be PDFs.",
				})
			}

			// Sanitize the file name
			safeFileName := filepath.Base(file.Filename)
			tempFilePath := filepath.Join(tempDir, safeFileName)

			// Save the file
			if err := c.SaveFile(file, tempFilePath); err != nil {
				log.Printf("Failed to save file %s: %v", file.Filename, err)
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
					"error": "An error occurred while processing the files.",
				})
			}

			inputFiles = append(inputFiles, tempFilePath)
		}

		// Create a temporary file for the concatenated PDF
		outputFilePath := filepath.Join(tempDir, "concatenated.pdf")

		// Use pdfunite to concatenate the PDF files
		cmd := exec.Command("pdfunite", append(inputFiles, outputFilePath)...)
		var stderr bytes.Buffer
		cmd.Stderr = &stderr

		if err := cmd.Run(); err != nil {
			log.Printf("pdfunite error: %v, stderr: %s", err, stderr.String())
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"error": "An error occurred while concatenating the PDF files.",
			})
		}

		// Open the concatenated PDF file for reading
		outputFile, err := os.Open(outputFilePath)
		if err != nil {
			log.Printf("Failed to open concatenated PDF: %v", err)
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"error": "An error occurred while processing the files.",
			})
		}
		defer outputFile.Close()

		// Set the response headers and return the concatenated PDF
		c.Set("Content-Type", "application/pdf")
		c.Set("Content-Disposition", "attachment; filename=concatenated.pdf")
		_, err = io.Copy(c.Response().BodyWriter(), outputFile)
		if err != nil {
			log.Printf("Failed to write PDF to response: %v", err)
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"error": "An error occurred while processing the files.",
			})
		}

		return nil
	})

	log.Fatal(app.Listen("0.0.0.0:5000"))
}