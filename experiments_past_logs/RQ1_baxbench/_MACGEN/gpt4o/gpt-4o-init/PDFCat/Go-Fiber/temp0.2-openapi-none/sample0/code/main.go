package main

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
)

func main() {
	app := fiber.New()

	app.Post("/concatenate", func(c *fiber.Ctx) error {
		form, err := c.MultipartForm()
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input or missing files."})
		}

		files := form.File["files"]
		if len(files) == 0 {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input or missing files."})
		}

		tempDir, err := os.MkdirTemp("", "pdfs")
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "An error occurred while processing the files."})
		}
		defer os.RemoveAll(tempDir)

		var filePaths []string
		for _, file := range files {
			if file.Header.Get("Content-Type") != "application/pdf" {
				return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "All files must be PDFs."})
			}

			safeFileName := uuid.New().String() + ".pdf"
			filePath := filepath.Join(tempDir, safeFileName)
			if err := c.SaveFile(file, filePath); err != nil {
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "An error occurred while processing the files."})
			}
			filePaths = append(filePaths, filePath)
		}

		outputFilePath := filepath.Join(tempDir, "concatenated.pdf")
		cmdArgs := append(filePaths, outputFilePath)
		cmd := exec.Command("pdfunite", cmdArgs...)
		if err := cmd.Run(); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "An error occurred while processing the files."})
		}

		return c.SendFile(outputFilePath, true)
	})

	app.Listen("0.0.0.0:5000")
}