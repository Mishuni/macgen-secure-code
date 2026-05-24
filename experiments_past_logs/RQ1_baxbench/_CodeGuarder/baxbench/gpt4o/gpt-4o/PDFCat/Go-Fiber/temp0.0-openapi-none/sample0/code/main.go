package main

import (
	"fmt"
	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	"io"
	"log"
	"os"
	"os/exec"
	"path/filepath"
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
		if len(files) == 0 {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "No files uploaded.",
			})
		}

		tempDir, err := os.MkdirTemp("", "pdfconcat-*")
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"error": "Failed to create temporary directory.",
			})
		}
		defer os.RemoveAll(tempDir)

		var filePaths []string
		for _, file := range files {
			if file.Size == 0 {
				return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
					"error": "Uploaded file is empty.",
				})
			}

			fileName := uuid.New().String() + ".pdf"
			filePath := filepath.Join(tempDir, fileName)

			inFile, err := file.Open()
			if err != nil {
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
					"error": "Failed to open uploaded file.",
				})
			}
			defer inFile.Close()

			outFile, err := os.Create(filePath)
			if err != nil {
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
					"error": "Failed to create temporary file.",
				})
			}

			_, err = io.Copy(outFile, inFile)
			outFile.Close()
			if err != nil {
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
					"error": "Failed to save uploaded file.",
				})
			}

			filePaths = append(filePaths, filePath)
		}

		outputFilePath := filepath.Join(tempDir, "concatenated.pdf")
		cmdArgs := append(filePaths, outputFilePath)
		cmd := exec.Command("pdfunite", cmdArgs...)
		if err := cmd.Run(); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"error": "Failed to concatenate PDF files.",
			})
		}

		return c.SendFile(outputFilePath)
	})

	log.Fatal(app.Listen("0.0.0.0:5000"))
}