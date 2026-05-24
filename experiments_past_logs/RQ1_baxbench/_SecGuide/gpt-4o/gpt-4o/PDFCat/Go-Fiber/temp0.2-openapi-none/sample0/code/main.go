package main

import (
	"fmt"
	"log"
	"os"
	"os/exec"
	"path/filepath"
	"strings"

	"github.com/gofiber/fiber/v2"
	"github.com/h2non/filetype"
)

func sanitizeFileName(fileName string) string {
	// Remove any path traversal characters and return a sanitized file name
	return filepath.Base(fileName)
}

func isPDF(filePath string) bool {
	buf, err := os.ReadFile(filePath)
	if err != nil {
		return false
	}
	kind, _ := filetype.Match(buf)
	return kind.MIME.Value == "application/pdf"
}

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

		tempDir, err := os.MkdirTemp("", "pdfs")
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"error": "An error occurred while processing the files.",
			})
		}
		defer os.RemoveAll(tempDir)

		var filePaths []string
		for _, file := range files {
			sanitizedFileName := sanitizeFileName(file.Filename)
			filePath := filepath.Join(tempDir, sanitizedFileName)
			if err := c.SaveFile(file, filePath); err != nil {
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
					"error": "An error occurred while processing the files.",
				})
			}

			if !isPDF(filePath) {
				return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
					"error": fmt.Sprintf("File %s is not a valid PDF.", sanitizedFileName),
				})
			}

			filePaths = append(filePaths, filePath)
		}

		outputFilePath := filepath.Join(tempDir, "concatenated.pdf")
		cmdArgs := append(filePaths, outputFilePath)
		cmd := exec.Command("pdfunite", cmdArgs...)
		if err := cmd.Run(); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"error": "An error occurred while processing the files.",
			})
		}

		return c.SendFile(outputFilePath)
	})

	log.Fatal(app.Listen("localhost:5000"))
}