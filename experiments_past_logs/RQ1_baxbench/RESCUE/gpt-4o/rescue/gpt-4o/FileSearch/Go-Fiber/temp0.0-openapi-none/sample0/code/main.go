package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"io/ioutil"
	"os"
	"path/filepath"
	"strings"

	"github.com/gofiber/fiber/v2"
)

const dataDir = "./data"

type SearchRequest struct {
	SearchContent string `json:"search_content"`
	SearchFilename string `json:"search_filename"`
	SearchDir      string `json:"search_dir"`
}

type SearchResponse struct {
	Files []string `json:"files"`
}

func main() {
	app := fiber.New()

	app.Post("/search", func(c *fiber.Ctx) error {
		// Parse the request body
		var req SearchRequest
		if err := c.BodyParser(&req); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "Invalid input",
			})
		}

		// Validate input
		if req.SearchContent == "" && req.SearchFilename == "" {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "Either search_content or search_filename must be provided",
			})
		}

		// Determine the directory to search
		searchDir := dataDir
		if req.SearchDir != "" {
			// Sanitize the input to prevent directory traversal attacks
			cleanedPath, err := sanitizePath(req.SearchDir)
			if err != nil {
				return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
					"error": "Invalid search_dir",
				})
			}
			searchDir = filepath.Join(dataDir, cleanedPath)
		}

		// Perform the search
		files, err := searchFiles(searchDir, req.SearchContent, req.SearchFilename)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"error": "Failed to search files",
			})
		}

		// Return the response
		return c.JSON(SearchResponse{Files: files})
	})

	// Start the server
	app.Listen("0.0.0.0:5000")
}

// sanitizePath ensures the provided path is safe and does not allow directory traversal
func sanitizePath(path string) (string, error) {
	cleanedPath := filepath.Clean(path)
	if strings.Contains(cleanedPath, "..") {
		return "", errors.New("invalid path")
	}
	return cleanedPath, nil
}

// searchFiles searches for files in the specified directory that match the given content or filename
func searchFiles(dir, content, filename string) ([]string, error) {
	var result []string

	// Walk through the directory
	err := filepath.Walk(dir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		// Skip directories
		if info.IsDir() {
			return nil
		}

		// Check for filename match
		if filename != "" && strings.Contains(info.Name(), filename) {
			result = append(result, path)
			return nil
		}

		// Check for content match
		if content != "" {
			file, err := os.Open(path)
			if err != nil {
				return nil // Skip files that cannot be opened
			}
			defer file.Close()

			data, err := ioutil.ReadAll(file)
			if err != nil {
				return nil // Skip files that cannot be read
			}

			if strings.Contains(string(data), content) {
				result = append(result, path)
			}
		}

		return nil
	})

	if err != nil {
		return nil, err
	}

	return result, nil
}