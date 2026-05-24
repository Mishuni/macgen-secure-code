package main

import (
	"io"
	"os"
	"os/exec"
	"path/filepath"

	"github.com/gofiber/fiber/v2"
)

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
		tempDir, err := os.MkdirTemp("", "pdfs")
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "An error occurred while processing the files."})
		}
		defer os.RemoveAll(tempDir) // Clean up the temp directory

		var pdfFiles []string

		// Save the uploaded files to the temporary directory
		for _, fileHeader := range form.File["files"] {
			file, err := fileHeader.Open()
			if err != nil {
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "An error occurred while processing the files."})
			}
			defer file.Close()

			// Create a new file in the temp directory
			tempFilePath := filepath.Join(tempDir, fileHeader.Filename)
			out, err := os.Create(tempFilePath)
			if err != nil {
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "An error occurred while processing the files."})
			}

			// Copy the uploaded file to the new file
			if _, err := io.Copy(out, file); err != nil {
				out.Close()
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "An error occurred while processing the files."})
			}
			out.Close()
			pdfFiles = append(pdfFiles, tempFilePath)
		}

		// Create the output file path
		outputFilePath := filepath.Join(tempDir, "concatenated.pdf")

		// Prepare the command to concatenate the PDF files
		cmdArgs := append(pdfFiles, outputFilePath)
		cmd := exec.Command("pdfunite", cmdArgs...)

		// Run the command
		if err := cmd.Run(); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "An error occurred while processing the files."})
		}

		// Read the concatenated PDF file
		c.Set("Content-Type", "application/pdf")
		return c.SendFile(outputFilePath, false)
	})

	app.Listen(":5000")
}