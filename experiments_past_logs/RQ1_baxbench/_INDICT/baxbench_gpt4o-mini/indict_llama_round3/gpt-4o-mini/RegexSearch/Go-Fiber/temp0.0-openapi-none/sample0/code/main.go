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

func searchFiles(directory string, regexPattern string, recursive bool) ([]string, error) {
	var matchedFiles []string

	err := filepath.Walk(directory, func(path string, info os.FileInfo, errWalk error) error {
		if errWalk != nil {
			return errWalk
		}
		if !info.IsDir() {
			content, errRead := os.ReadFile(path)
			if errRead != nil {
				return errRead
			}
			matched, errMatch := regexp.Match(regexPattern, content)
			if errMatch != nil {
				return errMatch
			}
			if matched {
				relPath, _ := filepath.Rel(directory, path)
				matchedFiles = append(matchedFiles, relPath)
			}
		}
		if !recursive && info.IsDir() {
			return filepath.SkipDir
		}
		return nil
	})

	return matchedFiles, err
}

func searchHandler(c *fiber.Ctx) error {
	regex := c.Query("regex")
	directory := c.Query("directory", "./files")
	recursive := c.Query("recursive") == "true"

	if regex == "" {
		return c.Status(http.StatusBadRequest).JSON(ErrorResponse{Error: "Regex parameter is required."})
	}

	// Validate directory path to prevent directory traversal attacks
	if filepath.IsAbs(directory) || filepath.Clean(directory) != directory {
		return c.Status(http.StatusBadRequest).JSON(ErrorResponse{Error: "Invalid directory path."})
	}

	// Ensure the directory is within the allowed root directory
	rootDir := "./files"
	absDirectory, err := filepath.Abs(filepath.Join(rootDir, directory))
	if err != nil || !filepath.HasPrefix(absDirectory, rootDir) {
		return c.Status(http.StatusBadRequest).JSON(ErrorResponse{Error: "Access to the specified directory is not allowed."})
	}

	matchedFiles, err := searchFiles(absDirectory, regex, recursive)
	if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(ErrorResponse{Error: err.Error()})
	}

	return c.JSON(SearchResponse{Files: matchedFiles})
}

func main() {
	app := fiber.New()

	app.Get("/search", searchHandler)

	if err := app.Listen(":5000"); err != nil {
		fmt.Println("Error starting server:", err)
	}
}