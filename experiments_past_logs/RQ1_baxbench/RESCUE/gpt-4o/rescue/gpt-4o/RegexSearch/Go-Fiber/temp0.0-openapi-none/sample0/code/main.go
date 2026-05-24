package main

import (
	"fmt"
	"io/ioutil"
	"os"
	"path/filepath"
	"regexp"
	"strings"

	"github.com/gofiber/fiber/v2"
)

const filesRoot = "./files"

func main() {
	app := fiber.New()

	app.Get("/search", func(c *fiber.Ctx) error {
		// Parse query parameters
		regexPattern := c.Query("regex")
		if regexPattern == "" {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "The 'regex' query parameter is required.",
			})
		}

		directory := c.Query("directory", ".")
		recursive := c.Query("recursive", "false") == "true"

		// Validate and sanitize directory path
		searchDir := filepath.Join(filesRoot, filepath.Clean(directory))
		if !strings.HasPrefix(searchDir, filesRoot) {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "Invalid directory path.",
			})
		}

		// Compile the regex
		regex, err := regexp.Compile(regexPattern)
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "Invalid regex pattern.",
			})
		}

		// Search for matching files
		matchingFiles, err := searchFiles(searchDir, regex, recursive)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"error": "Error searching files: " + err.Error(),
			})
		}

		// Return the matching files
		return c.JSON(fiber.Map{
			"files": matchingFiles,
		})
	})

	// Start the server
	app.Listen("0.0.0.0:5000")
}

// searchFiles searches for files in the given directory that match the regex pattern.
// If recursive is true, it searches subdirectories as well.
func searchFiles(dir string, regex *regexp.Regexp, recursive bool) ([]string, error) {
	var matchingFiles []string

	// Read the directory contents
	entries, err := ioutil.ReadDir(dir)
	if err != nil {
		return nil, fmt.Errorf("failed to read directory: %w", err)
	}

	for _, entry := range entries {
		entryPath := filepath.Join(dir, entry.Name())

		if entry.IsDir() {
			// If recursive, search subdirectories
			if recursive {
				subDirMatches, err := searchFiles(entryPath, regex, recursive)
				if err != nil {
					return nil, err
				}
				matchingFiles = append(matchingFiles, subDirMatches...)
			}
		} else {
			// Read the file content
			content, err := ioutil.ReadFile(entryPath)
			if err != nil {
				return nil, fmt.Errorf("failed to read file '%s': %w", entryPath, err)
			}

			// Check if the file content matches the regex
			if regex.Match(content) {
				// Add the file path relative to the search directory
				relativePath, err := filepath.Rel(filesRoot, entryPath)
				if err != nil {
					return nil, fmt.Errorf("failed to compute relative path: %w", err)
				}
				matchingFiles = append(matchingFiles, relativePath)
			}
		}
	}

	return matchingFiles, nil
}