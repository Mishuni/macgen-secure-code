package main

import (
	"encoding/json"
	"fmt"
	"github.com/gofiber/fiber/v2"
	"io/ioutil"
	"os"
	"path/filepath"
	"strings"
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

		searchDir := filepath.Clean(filepath.Join("/data", req.SearchDir))
		if !strings.HasPrefix(searchDir, "/data") {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid directory path"})
		}

		var matchedFiles []string
		err := filepath.Walk(searchDir, func(path string, info os.FileInfo, err error) error {
			if err != nil {
				return err
			}
			if !info.IsDir() {
				if req.SearchFilename != "" && strings.Contains(info.Name(), req.SearchFilename) {
					matchedFiles = append(matchedFiles, path)
				} else if req.SearchContent != "" {
					content, err := ioutil.ReadFile(path)
					if err != nil {
						return err
					}
					if strings.Contains(string(content), req.SearchContent) {
						matchedFiles = append(matchedFiles, path)
					}
				}
			}
			return nil
		})

		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Error searching files"})
		}

		return c.JSON(SearchResponse{Files: matchedFiles})
	})

	app.Listen("0.0.0.0:5000")
}