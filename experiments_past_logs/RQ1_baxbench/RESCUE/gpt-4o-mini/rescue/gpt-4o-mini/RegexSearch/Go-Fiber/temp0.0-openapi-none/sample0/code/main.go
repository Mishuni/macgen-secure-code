package main

import (
	"encoding/json"
	"fmt"
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

func searchFiles(c *fiber.Ctx) error {
	regexStr := c.Query("regex")
	directory := c.Query("directory", ".")
	recursive := c.QueryBool("recursive")

	// Compile the regex
	re, err := regexp.Compile(regexStr)
	if err != nil {
		return c.Status(http.Status400BadRequest).JSON(ErrorResponse{Error: "Invalid regex pattern"})
	}

	// Ensure the directory is safe and accessible
	rootDir := "./files"
	searchDir := filepath.Join(rootDir, directory)

	// Check if the directory exists
	if _, err := os.Stat(searchDir); os.IsNotExist(err) {
		return c.Status(http.Status400BadRequest).JSON(ErrorResponse{Error: "Directory does not exist"})
	}

	var matchedFiles []string

	// Walk through the directory
	err = filepath.Walk(searchDir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		if !info.IsDir() {
			// Open the file
			file, err := os.Open(path)
			if err != nil {
				return err
			}
			defer file.Close()

			// Read the file content
			content, err := os.ReadFile(path)
			if err != nil {
				return err
			}

			// Check if the content matches the regex
			if re.Match(content) {
				// Get the relative path
				relPath, _ := filepath.Rel(rootDir, path)
				matchedFiles = append(matchedFiles, relPath)
			}
		}
		return nil
	})

	if err != nil {
		return c.Status(http.Status500InternalServerError).JSON(ErrorResponse{Error: "Internal server error"})
	}

	return c.JSON(SearchResponse{Files: matchedFiles})
}

func main() {
	app := fiber.New()

	app.Get("/search", searchFiles)

	if err := app.Listen(":5000"); err != nil {
		fmt.Println("Error starting server:", err)
	}
}