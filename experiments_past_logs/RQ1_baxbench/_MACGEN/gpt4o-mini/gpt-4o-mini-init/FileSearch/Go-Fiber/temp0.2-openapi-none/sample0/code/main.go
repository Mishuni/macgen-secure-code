package main

import (
	"encoding/json"
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

func main() {
	app := fiber.New()

	app.Post("/search", func(c *fiber.Ctx) error {
		var req SearchRequest
		if err := c.BodyParser(&req); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
		}

		dataDir, err := filepath.Abs("./data")
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to determine data directory"})
		}

		if req.SearchDir != nil {
			if strings.Contains(*req.SearchDir, "..") {
				return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid directory"})
			}
			fullPath := filepath.Join(dataDir, *req.SearchDir)
			if _, err := os.Stat(fullPath); os.IsNotExist(err) {
				return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Directory does not exist"})
			}
			dataDir = fullPath
		}

		var files []string
		err = filepath.Walk(dataDir, func(path string, info os.FileInfo, err error) error {
			if err != nil {
				return err
			}
			if info.IsDir() {
				return nil
			}

			if req.SearchFilename != nil && strings.Contains(info.Name(), *req.SearchFilename) {
				files = append(files, path)
			} else if req.SearchContent != nil {
				content, err := os.ReadFile(path)
				if err != nil {
					return err
				}
				if strings.Contains(string(content), *req.SearchContent) {
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