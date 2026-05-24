package main

import (
	"encoding/json"
	"os"
	"path/filepath"
	"strings"

	"github.com/gofiber/fiber/v2"
)

type SearchRequest struct {
	SearchContent   *string `json:"search_content"`
	SearchFilename  *string `json:"search_filename"`
	SearchDir       *string `json:"search_dir"`
}

type SearchResponse struct {
	Files []string `json:"files"`
}

func main() {
	app := fiber.New()

	app.Post("/search", func(c *fiber.Ctx) error {
		var req SearchRequest
		if err := c.BodyParser(&req); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
		}

		dataDir := "./data"
		if req.SearchDir != nil {
			// Sanitize the search_dir to prevent directory traversal
			if strings.Contains(*req.SearchDir, "..") || strings.Contains(*req.SearchDir, "/") {
				return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid directory"})
			}
			dataDir = filepath.Join(dataDir, *req.SearchDir)
		}

		var files []string

		err := filepath.Walk(dataDir, func(path string, info os.FileInfo, err error) error {
			if err != nil {
				return err
			}
			if info.IsDir() {
				return nil
			}

			if req.SearchFilename != nil && strings.Contains(info.Name(), *req.SearchFilename) {
				files = append(files, path)
			}

			if req.SearchContent != nil {
				content, err := os.ReadFile(path)
				if err == nil && strings.Contains(string(content), *req.SearchContent) {
					files = append(files, path)
				}
			}

			return nil
		})

		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Error reading files"})
		}

		return c.JSON(SearchResponse{Files: files})
	})

	app.Listen(":5000")
}