package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"github.com/gofiber/fiber/v2"
)

const dataDir = "./data"

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
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
		}

		searchDir := dataDir
		if req.SearchDir != nil {
			// Sanitize and validate the search directory
			if !isValidDirectory(*req.SearchDir) {
				return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid directory"})
			}
			searchDir = filepath.Join(dataDir, *req.SearchDir)
		}

		files, err := searchFiles(searchDir, req.SearchContent, req.SearchFilename)
		if err != nil {
			return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Internal server error"})
		}

		return c.JSON(SearchResponse{Files: files})
	})

	app.Listen(":5000")
}

func isValidDirectory(dir string) bool {
	// Ensure the directory is relative and does not contain any path traversal characters
	absPath, err := filepath.Abs(dir)
	if err != nil {
		return false
	}
	return strings.HasPrefix(absPath, filepath.Join(dataDir, "")) // Ensure it is within the data directory
}

func searchFiles(searchDir string, content *string, filename *string) ([]string, error) {
	var matchedFiles []string

	err := filepath.Walk(searchDir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		if info.IsDir() {
			return nil
		}

		if filename != nil && !strings.Contains(info.Name(), *filename) {
			return nil
		}

		if content != nil {
			fileContent, err := ioutil.ReadFile(path)
			if err != nil {
				return err
			}
			if !strings.Contains(string(fileContent), *content) {
				return nil
			}
		}

		matchedFiles = append(matchedFiles, path)
		return nil
	})

	if err != nil {
		return nil, err
	}

	return matchedFiles, nil
}