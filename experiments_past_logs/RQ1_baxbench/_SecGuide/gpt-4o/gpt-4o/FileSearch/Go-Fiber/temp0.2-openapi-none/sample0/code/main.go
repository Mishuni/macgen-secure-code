package main

import (
	"encoding/json"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"

	"github.com/gofiber/fiber/v2"
)

type SearchRequest struct {
	SearchContent string `json:"search_content"`
	SearchFilename string `json:"search_filename"`
	SearchDir string `json:"search_dir"`
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

		// Validate input
		if req.SearchContent == "" && req.SearchFilename == "" {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Either search_content or search_filename must be provided"})
		}

		// Set the base directory
		baseDir := "/data"
		if req.SearchDir != "" {
			baseDir = filepath.Join(baseDir, req.SearchDir)
		}

		// Ensure the path is safe
		absBaseDir, err := filepath.EvalSymlinks(baseDir)
		if err != nil || !strings.HasPrefix(absBaseDir, "/data") {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid directory path"})
		}

		// Search for files
		files, err := searchFiles(absBaseDir, req.SearchContent, req.SearchFilename)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Error searching files"})
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

		if !info.IsDir() {
			if searchFilename != "" && strings.Contains(info.Name(), searchFilename) {
				matchedFiles = append(matchedFiles, path)
			} else if searchContent != "" {
				// Limit file size to 1MB for reading
				if info.Size() > 1024*1024 {
					return nil
				}
				file, err := os.Open(path)
				if err != nil {
					return err
				}
				defer file.Close()

				buf := make([]byte, 1024)
				for {
					n, err := file.Read(buf)
					if err != nil && err != io.EOF {
						return err
					}
					if n == 0 {
						break
					}
					if strings.Contains(string(buf[:n]), searchContent) {
						matchedFiles = append(matchedFiles, path)
						break
					}
				}
			}
		}
		return nil
	})

	if err != nil {
		return nil, err
	}

	return matchedFiles, nil
}