package main

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"regexp"
	"strings"

	"github.com/gofiber/fiber/v2"
)

const filesRoot = "./files"

func main() {
	app := fiber.New()

	app.Get("/search", func(c *fiber.Ctx) error {
		regexPattern := c.Query("regex")
		if regexPattern == "" {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "Regex pattern is required",
			})
		}

		directory := c.Query("directory", ".")
		recursive := c.Query("recursive", "false") == "true"

		// Validate and sanitize directory input
		if strings.Contains(directory, "..") {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "Invalid directory path",
			})
		}

		searchPath := filepath.Join(filesRoot, directory)
		if _, err := os.Stat(searchPath); os.IsNotExist(err) {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "Directory does not exist",
			})
		}

		// Compile the regex pattern
		regex, err := regexp.Compile(regexPattern)
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "Invalid regex pattern",
			})
		}

		// Search for files
		matchingFiles, err := searchFiles(searchPath, regex, recursive)
		if err != nil {
			log.Printf("Error searching files: %v", err)
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"error": "Internal server error",
			})
		}

		return c.JSON(fiber.Map{
			"files": matchingFiles,
		})
	})

	log.Fatal(app.Listen("0.0.0.0:5000"))
}

func searchFiles(root string, regex *regexp.Regexp, recursive bool) ([]string, error) {
	var matchingFiles []string

	err := filepath.Walk(root, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		if !info.IsDir() {
			// Read file content
			content, err := os.ReadFile(path)
			if err != nil {
				return err
			}

			// Check if file content matches the regex
			if regex.Match(content) {
				relativePath, err := filepath.Rel(filesRoot, path)
				if err != nil {
					return err
				}
				matchingFiles = append(matchingFiles, relativePath)
			}
		} else if !recursive && path != root {
			return filepath.SkipDir
		}

		return nil
	})

	return matchingFiles, err
}