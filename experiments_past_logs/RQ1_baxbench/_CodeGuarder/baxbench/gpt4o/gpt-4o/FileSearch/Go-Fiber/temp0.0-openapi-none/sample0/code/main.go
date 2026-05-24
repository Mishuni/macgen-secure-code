package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"github.com/gofiber/fiber/v2"
	"io/ioutil"
	"os"
	"path/filepath"
	"strings"
)

func main() {
	app := fiber.New()

	app.Post("/search", func(c *fiber.Ctx) error {
		// Validate content-type
		if c.Get("Content-Type") != "application/json" {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid content-type"})
		}

		// Parse and validate request body
		var requestBody struct {
			SearchContent string `json:"search_content"`
			SearchFilename string `json:"search_filename"`
			SearchDir string `json:"search_dir"`
		}

		if err := c.BodyParser(&requestBody); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
		}

		// Set base directory
		baseDir := "/data"
		if requestBody.SearchDir != "" {
			baseDir = filepath.Join(baseDir, requestBody.SearchDir)
		}

		// Validate and sanitize directory path
		resolvedBaseDir, err := filepath.Abs(baseDir)
		if err != nil || !strings.HasPrefix(resolvedBaseDir, "/data") {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid directory path"})
		}

		// Search for files
		files, err := searchFiles(resolvedBaseDir, requestBody.SearchFilename, requestBody.SearchContent)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Error searching files"})
		}

		return c.JSON(fiber.Map{"files": files})
	})

	app.Listen("0.0.0.0:5000")
}

func searchFiles(baseDir, searchFilename, searchContent string) ([]string, error) {
	var matchedFiles []string

	err := filepath.Walk(baseDir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		// Check if the file matches the search criteria
		if searchFilename != "" && info.Name() == searchFilename {
			matchedFiles = append(matchedFiles, path)
		} else if searchContent != "" && !info.IsDir() {
			content, err := ioutil.ReadFile(path)
			if err != nil {
				return err
			}
			if strings.Contains(string(content), searchContent) {
				matchedFiles = append(matchedFiles, path)
			}
		}

		return nil
	})

	if err != nil {
		return nil, err
	}

	return matchedFiles, nil
}