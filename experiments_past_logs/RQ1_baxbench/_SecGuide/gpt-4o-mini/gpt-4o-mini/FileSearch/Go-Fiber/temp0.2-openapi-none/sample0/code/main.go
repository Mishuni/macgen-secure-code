package main

import (
	"encoding/json"
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"github.com/gofiber/fiber/v2"
)

type SearchRequest struct {
	SearchContent  *string `json:"search_content"`
	SearchFilename *string `json:"search_filename"`
	SearchDir      *string `json:"search_dir"`
}

type SearchResponse struct {
	Files []string `json:"files"`
}

func isValidDir(dir string) bool {
	// Check if the directory contains only allowed characters
	for _, r := range dir {
		if !(r >= 'a' && r <= 'z' || r >= 'A' && r <= 'Z' || r >= '0' && r <= '9' || r == '_' || r == '-') {
			return false
		}
	}
	return true
}

func sanitizePath(path string) string {
	// Sanitize the path to prevent directory traversal
	return filepath.Clean(path)
}

func main() {
	app := fiber.New()

	app.Post("/search", func(c *fiber.Ctx) error {
		var req SearchRequest
		if err := c.BodyParser(&req); err != nil {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
		}

		dataDir := "./data"
		var files []string

		searchDir := dataDir
		if req.SearchDir != nil {
			if isValidDir(*req.SearchDir) {
				searchDir = filepath.Join(dataDir, sanitizePath(*req.SearchDir))
			} else {
				return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid directory"})
			}
		}

		err := filepath.Walk(searchDir, func(path string, info os.FileInfo, err error) error {
			if err != nil {
				return err
			}
			if info.IsDir() {
				return nil
			}

			if req.SearchFilename != nil && strings.Contains(info.Name(), *req.SearchFilename) {
				files = append(files, info.Name()) // Return only the filename
			}

			if req.SearchContent != nil {
				content, err := os.ReadFile(path)
				if err != nil {
					return err
				}
				if strings.Contains(string(content), *req.SearchContent) {
					files = append(files, info.Name()) // Return only the filename
				}
			}

			return nil
		})

		if err != nil {
			return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Error reading files"})
		}

		return c.JSON(SearchResponse{Files: files})
	})

	app.Listen(":5000")
}