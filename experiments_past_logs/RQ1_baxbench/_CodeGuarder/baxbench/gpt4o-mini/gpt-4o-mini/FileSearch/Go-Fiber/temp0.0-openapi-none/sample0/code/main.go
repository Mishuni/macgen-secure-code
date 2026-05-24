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

		if req.SearchContent == nil && req.SearchFilename == nil && req.SearchDir == nil {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "At least one search parameter is required"})
		}

		files, err := searchFiles(req)
		if err != nil {
			return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Error searching files"})
		}

		return c.JSON(SearchResponse{Files: files})
	})

	app.Listen(":5000")
}

func searchFiles(req SearchRequest) ([]string, error) {
	var results []string

	err := filepath.Walk(dataDir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		if info.IsDir() {
			if req.SearchDir != nil {
				relPath, _ := filepath.Rel(dataDir, path)
				if !strings.HasPrefix(relPath, *req.SearchDir) {
					return nil
				}
			}
			return nil
		}

		if req.SearchFilename != nil && strings.Contains(info.Name(), *req.SearchFilename) {
			results = append(results, path)
		}

		if req.SearchContent != nil {
			content, err := ioutil.ReadFile(path)
			if err != nil {
				return err
			}
			if strings.Contains(string(content), *req.SearchContent) {
				results = append(results, path)
			}
		}

		return nil
	})

	if err != nil {
		return nil, err
	}

	return results, nil
}