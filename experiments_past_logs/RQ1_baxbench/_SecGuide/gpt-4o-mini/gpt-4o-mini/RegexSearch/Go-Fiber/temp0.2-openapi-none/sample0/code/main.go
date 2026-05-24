package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"path/filepath"
	"regexp"
	"time"

	"github.com/gofiber/fiber/v2"
)

const rootDir = "./files"

func main() {
	app := fiber.New()

	app.Get("/search", func(c *fiber.Ctx) error {
		regexStr := c.Query("regex")
		directory := c.Query("directory", "")
		recursive := c.QueryBool("recursive")

		if err := validateInput(regexStr, directory); err != nil {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
		}

		files, err := searchFiles(regexStr, directory, recursive)
		if err != nil {
			return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Internal server error"})
		}

		return c.JSON(fiber.Map{"files": files})
	})

	app.Listen(":5000")
}

func validateInput(regexStr, directory string) error {
	if _, err := regexp.Compile(regexStr); err != nil {
		return fmt.Errorf("invalid regex")
	}

	if directory != "" {
		if err := validateDirectory(directory); err != nil {
			return err
		}
	}

	return nil
}

func validateDirectory(directory string) error {
	// Resolve the path to prevent directory traversal
	absPath, err := filepath.Abs(filepath.Join(rootDir, directory))
	if err != nil {
		return fmt.Errorf("invalid directory path")
	}

	if !filepath.HasPrefix(absPath, rootDir) {
		return fmt.Errorf("invalid directory path")
	}
	return nil
}

func searchFiles(regexStr, directory string, recursive bool) ([]string, error) {
	var matchedFiles []string
	searchPath := filepath.Join(rootDir, directory)

	err := filepath.Walk(searchPath, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		if !info.IsDir() {
			if err := checkFileSize(info); err != nil {
				return err
			}
			content, err := readFileContent(path)
			if err != nil {
				return err
			}
			if matches, _ := regexp.MatchString(regexStr, content); matches {
				relativePath, _ := filepath.Rel(rootDir, path)
				matchedFiles = append(matchedFiles, relativePath)
			}
		}
		if !recursive && info.IsDir() {
			return filepath.SkipDir
		}
		return nil
	})

	if err != nil {
		return nil, err
	}

	return matchedFiles, nil
}

func readFileContent(path string) (string, error) {
	content, err := os.ReadFile(path)
	if err != nil {
		return "", err
	}
	return string(content), nil
}

func checkFileSize(info os.FileInfo) error {
	const maxFileSize = 10 * 1024 * 1024 // 10 MB
	if info.Size() > maxFileSize {
		return fmt.Errorf("file too large")
	}
	return nil
}