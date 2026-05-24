package main

import (
	"fmt"
	"io/ioutil"
	"os"
	"os/exec"
	"path/filepath"

	"github.com/gofiber/fiber/v2"
)

const storageDir = "./uploads/"

func main() {
	app := fiber.New()

	// Create storage directory if it doesn't exist
	if err := os.MkdirAll(storageDir, os.ModePerm); err != nil {
		fmt.Println("Error creating storage directory:", err)
		return
	}

	app.Post("/concatenate", func(c *fiber.Ctx) error {
		// Parse the multipart form
		if err := c.BodyParser(&fiber.FormData{}); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input or missing files."})
		}

		// Get the files from the request
		form, err := c.MultipartForm()
		if err != nil || len(form.File["files"]) == 0 {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input or missing files."})
		}

		// Create a slice to hold the file paths
		var filePaths []string

		// Save the uploaded files to the storage directory
		for _, fileHeader := range form.File["files"] {
			filePath := filepath.Join(storageDir, fileHeader.Filename)
			if err := c.SaveFile(fileHeader, filePath); err != nil {
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "An error occurred while processing the files."})
			}
			filePaths = append(filePaths, filePath)
		}

		// Define the output file path
		outputFilePath := filepath.Join(storageDir, "concatenated.pdf")

		// Prepare the command to concatenate PDF files
		cmdArgs := append(filePaths, outputFilePath)
		cmd := exec.Command("pdfunite", cmdArgs...)

		// Run the command
		if err := cmd.Run(); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "An error occurred while processing the files."})
		}

		// Read the concatenated PDF file
		outputFile, err := ioutil.ReadFile(outputFilePath)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "An error occurred while processing the files."})
		}

		// Return the concatenated PDF file
		c.Set("Content-Type", "application/pdf")
		return c.Send(outputFile)
	})

	app.Listen(":5000")
}