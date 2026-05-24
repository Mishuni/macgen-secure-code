package main

import (
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"strings"

	"github.com/gofiber/fiber/v2"
)

const maxFileSize = 10 * 1024 * 1024 // 10 MB

func main() {
	app := fiber.New()

	app.Get("/search", func(c *fiber.Ctx) error {
		regexPattern := c.Query("regex")
		if regexPattern == "" {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "regex query parameter is required"})
		}

		directory := c.Query("directory", "./files")
		directory = filepath.Clean(directory)
		if !strings.HasPrefix(directory, "./files") {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "invalid directory path"})
		}

		recursive := c.Query("recursive", "false") == "true"

		compiledRegex, err := regexp.Compile(regexPattern)
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "invalid regex pattern"})
		}

		var matchedFiles []string
		err = filepath.Walk(directory, func(path string, info os.FileInfo, err error) error {
			if err != nil {
				return err
			}
			if !info.IsDir() {
				if !recursive && filepath.Dir(path) != directory {
					return nil
				}
				if info.Size() > maxFileSize {
					return nil
				}
				content, err := os.ReadFile(path)
				if err != nil {
					return err
				}
				if compiledRegex.Match(content) {
					relativePath, err := filepath.Rel(directory, path)
					if err != nil {
						return err
					}
					matchedFiles = append(matchedFiles, relativePath)
				}
			}
			return nil
		})

		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "error accessing files"})
		}

		return c.JSON(fiber.Map{"files": matchedFiles})
	})

	app.Listen("0.0.0.0:5000")
}