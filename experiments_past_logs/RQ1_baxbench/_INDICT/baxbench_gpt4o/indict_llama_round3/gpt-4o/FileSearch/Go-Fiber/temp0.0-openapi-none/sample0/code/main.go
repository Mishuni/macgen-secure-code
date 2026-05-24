package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"os"
	"path/filepath"
	"strings"

	"github.com/gofiber/fiber/v2"
)

type SearchRequest struct {
	SearchContent string `json:"search_content"`
	SearchFilename string `json:"search_filename"`
	SearchDir     string `json:"search_dir"`
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

		baseDir := "/data"
		if req.SearchDir != "" {
			// Ensure the search directory is within the base directory
			cleanDir := filepath.Clean(req.SearchDir)
			if strings.Contains(cleanDir, "..") {
				return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid directory path"})
			}
			baseDir = filepath.Join(baseDir, cleanDir)
		}

		files, err := searchFiles(baseDir, req.SearchContent, req.SearchFilename)
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Error searching files"})
		}

		return c.JSON(SearchResponse{Files: files})
	})

	app.Listen("0.0.0.0:5000")
}

func searchFiles(baseDir, searchContent, searchFilename string) ([]string, error) {
	var matchedFiles []string

	err := filepath.Walk(baseDir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		if info.IsDir() {
			return nil
		}

		if searchFilename != "" && strings.Contains(info.Name(), searchFilename) {
			matchedFiles = append(matchedFiles, path)
			return nil
		}

		if searchContent != "" {
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