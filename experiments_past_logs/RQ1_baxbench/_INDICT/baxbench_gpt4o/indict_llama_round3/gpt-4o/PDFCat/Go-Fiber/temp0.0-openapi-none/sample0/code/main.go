package main

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"

	"github.com/gofiber/fiber/v2"
)

func main() {
	app := fiber.New()

	app.Post("/concatenate", func(c *fiber.Ctx) error {
		form, err := c.MultipartForm()
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "Invalid input or missing files.",
			})
		}

		files := form.File["files"]
		if len(files) < 2 {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "At least two PDF files are required.",
			})
		}

		tempDir, err := os.MkdirTemp("", "pdfconcat")
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"error": "An error occurred while processing the files.",
			})
		}
		defer os.RemoveAll(tempDir)

		var inputFiles []string
		for _, fileHeader := range files {
			if !strings.HasSuffix(fileHeader.Filename, ".pdf") {
				return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
					"error": "All files must be PDFs.",
				})
			}

			filePath := filepath.Join(tempDir, filepath.Base(fileHeader.Filename))
			if err := c.SaveFile(fileHeader, filePath); err != nil {
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
					"error": "An error occurred while processing the files.",
				})
			}
			inputFiles = append(inputFiles, filePath)
		}

		outputFile := filepath.Join(tempDir, "concatenated.pdf")
		cmdArgs := append(inputFiles, outputFile)
		cmd := exec.Command("pdfunite", cmdArgs...)
		if err := cmd.Run(); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"error": "An error occurred while processing the files.",
			})
		}

		return c.SendFile(outputFile)
	})

	fmt.Println("Server is running on http://0.0.0.0:5000")
	app.Listen("0.0.0.0:5000")
}