package main

import (
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
	"regexp"
	"strings"

	"github.com/gofiber/fiber/v2"
)

func main() {
	app := fiber.New()

	app.Get("/search", func(c *fiber.Ctx) error {
		regexPattern := c.Query("regex")
		if regexPattern == "" {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "regex query parameter is required",
			})
		}

		directory := c.Query("directory", "./files")
		if !strings.HasPrefix(directory, "./files") {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "access to the specified directory is not allowed",
			})
		}

		recursive := c.Query("recursive", "false") == "true"

		compiledRegex, err := regexp.Compile(regexPattern)
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "invalid regex pattern",
			})
		}

		var matchedFiles []string
		err = filepath.WalkDir(directory, func(path string, d fs.DirEntry, err error) error {
			if err != nil {
				return err
			}

			if !recursive && d.IsDir() && path != directory {
				return filepath.SkipDir
			}

			if !d.IsDir() {
				content, err := os.ReadFile(path)
				if err != nil {
					return err
				}

				if compiledRegex.Match(content) {
					relPath, err := filepath.Rel(directory, path)
					if err != nil {
						return err
					}
					matchedFiles = append(matchedFiles, relPath)
				}
			}
			return nil
		})

		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"error": fmt.Sprintf("error searching files: %v", err),
			})
		}

		return c.JSON(fiber.Map{
			"files": matchedFiles,
		})
	})

	app.Listen("0.0.0.0:5000")
}