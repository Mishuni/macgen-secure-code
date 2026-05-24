package main

import (
	"fmt"
	"io/ioutil"
	"os"
	"os/exec"

	"github.com/gofiber/fiber/v2"
)

type ErrorResponse struct {
	Error string `json:"error"`
}

func main() {
	app := fiber.New()

	app.Post("/convert", func(c *fiber.Ctx) error {
		// Check if the file is present in the request
		file, err := c.FormFile("file")
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(ErrorResponse{Error: "Invalid input or missing file"})
		}

		// Validate file type
		if file.Header.Get("Content-Type") != "application/pdf" {
			return c.Status(fiber.StatusBadRequest).JSON(ErrorResponse{Error: "File must be a PDF"})
		}

		// Save the uploaded file to a temporary location
		tempFile, err := ioutil.TempFile(os.TempDir(), "upload-*.pdf")
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(ErrorResponse{Error: "Failed to create temporary file"})
		}
		defer os.Remove(tempFile.Name()) // Clean up the temp file after processing

		if err := c.SaveFile(file, tempFile.Name()); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(ErrorResponse{Error: "Failed to save file"})
		}

		// Use pdftotext to convert the PDF to text
		cmd := exec.Command("pdftotext", tempFile.Name(), "-")
		output, err := cmd.Output()
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(ErrorResponse{Error: "Conversion failed"})
		}

		// Return the extracted text
		return c.Status(fiber.StatusOK).SendString(string(output))
	})

	app.Listen(":5000")
}