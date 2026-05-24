package main

import (
	"encoding/json"
	"net/http"
	"os"
	"path/filepath"
	"regexp"

	"github.com/gofiber/fiber/v2"
)

type SearchResponse struct {
	Files []string `json:"files"`
}

type ErrorResponse struct {
	Error string `json:"error"`
}

func main() {
	app := fiber.New()

	app.Get("/search", func(c *fiber.Ctx) error {
		regexStr := c.Query("regex")
		directory := c.Query("directory", "./files")
		recursive := c.Query("recursive", "false") == "true"

		// Validate regex
		if _, err := regexp.Compile(regexStr); err != nil {
			return c.Status(http.StatusBadRequest).JSON(ErrorResponse{Error: "Invalid regex pattern"})
		}

		// Sanitize and validate directory
		cleanedDir := filepath.Clean(directory)
		if !filepath.IsAbs(cleanedDir) {
			cleanedDir = filepath.Join("./files", cleanedDir)
		}
		if !isValidPath(cleanedDir) {
			return c.Status(http.StatusBadRequest).JSON(ErrorResponse{Error: "Invalid directory path"})
		}

		var files []string
		err := filepath.Walk(cleanedDir, func(path string, info os.FileInfo, err error) error {
			if err != nil {
				return err
			}
			if !info.IsDir() {
				content, err := os.ReadFile(path)
				if err != nil {
					return err
				}
				if matched, _ := regexp.Match(regexStr, content); matched {
					relPath, _ := filepath.Rel("./files", path)
					files = append(files, relPath)
				}
			}
			return nil
		})

		if err != nil {
			return c.Status(http.StatusInternalServerError).JSON(ErrorResponse{Error: "Error reading files"})
		}

		return c.JSON(SearchResponse{Files: files})
	})

	app.Listen(":5000")
}

func isValidPath(path string) bool {
	// Ensure the path starts with the root directory
	rootDir := filepath.Join(".", "files")
	absRootDir, _ := filepath.Abs(rootDir)
	absPath, _ := filepath.Abs(path)
	return filepath.HasPrefix(absPath, absRootDir)
}