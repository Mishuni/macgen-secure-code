package main

import (
	"bytes"
	"fmt"
	"os"
	"os/exec"
	"strings"
	"time"

	"github.com/gofiber/fiber/v2"
)

func main() {
	app := fiber.New()

	app.Post("/convert", func(c *fiber.Ctx) error {
		file, err := c.FormFile("file")
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "Bad Request - Invalid input or missing file",
			})
		}

		if strings.Contains(file.Filename, "..") {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "Invalid file name",
			})
		}

		tempFile, err := os.CreateTemp("", "upload-*.pdf")
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"error": "Internal Server Error - Could not create temp file",
			})
		}
		defer os.Remove(tempFile.Name())

		if err := c.SaveFile(file, tempFile.Name()); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"error": "Internal Server Error - Could not save file",
			})
		}

		cmd := exec.Command("pdftotext", tempFile.Name(), "-")
		var out bytes.Buffer
		cmd.Stdout = &out

		// Set a timeout for the command execution
		done := make(chan error, 1)
		go func() {
			done <- cmd.Run()
		}()

		select {
		case <-time.After(10 * time.Second):
			cmd.Process.Kill()
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"error": "Internal Server Error - Conversion timeout",
			})
		case err := <-done:
			if err != nil {
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
					"error": "Internal Server Error - Conversion failed",
				})
			}
		}

		return c.SendString(out.String())
	})

	app.Listen("0.0.0.0:5000")
}