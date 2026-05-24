package main

import (
	"fmt"
	"io/ioutil"
	"os"
	"os/exec"
	"path/filepath"

	"github.com/gofiber/fiber/v2"
)

func main() {
	app := fiber.New()

	app.Post("/concatenate", func(c *fiber.Ctx) error {
		// Handle multipart form data
		if err := c.Accepts("multipart/form-data"); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input or missing files."})
		}

		// Parse the form
		err := c.ParseMultipartForm(10 << 20) // Limit to 10 MB
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input or missing files."})
		}

		files := c.MultipartForm.File["files"]
		if len(files) == 0 {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input or missing files."})
		}

		// Create a temporary directory to store uploaded files
		tempDir, err := ioutil.TempDir("", "pdfs")
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "An error occurred while processing the files."})
		}
		defer os.RemoveAll(tempDir) // Clean up

		var inputFiles []string
		for _, fileHeader := range files {
			// Save the uploaded file to the temporary directory
			filePath := filepath.Join(tempDir, fileHeader.Filename)
			file, err := fileHeader.Open()
			if err != nil {
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "An error occurred while processing the files."})
			}
			defer file.Close()

			out, err := os.Create(filePath)
			if err != nil {
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "An error occurred while processing the files."})
			}
			defer out.Close()

			if _, err := io.Copy(out, file); err != nil {
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "An error occurred while processing the files."})
			}
			inputFiles = append(inputFiles, filePath)
		}

		// Prepare the output file path
		outputFile := filepath.Join(tempDir, "concatenated.pdf")

		// Use pdfunite to concatenate the PDF files
		cmd := exec.Command("pdfunite", append(inputFiles, outputFile)...)
		if err := cmd.Run(); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "An error occurred while processing the files."})
		}

		// Send the concatenated PDF back to the client
		c.Set("Content-Type", "application/pdf")
		return c.SendFile(outputFile, false)
	})

	app.Listen(":5000")
}