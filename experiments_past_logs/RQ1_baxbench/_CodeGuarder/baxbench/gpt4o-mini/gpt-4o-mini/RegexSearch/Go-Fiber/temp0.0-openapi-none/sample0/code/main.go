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

const rootDir = "./files"

func main() {
	app := fiber.New()

	app.Get("/search", searchHandler)

	if err := app.Listen(":5000"); err != nil {
		fmt.Println("Error starting server:", err)
	}
}

func searchHandler(c *fiber.Ctx) error {
	regexStr := c.Query("regex")
	directory := c.Query("directory", rootDir)
	recursive := c.QueryBool("recursive")

	if _, err := regexp.Compile(regexStr); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid regex pattern"})
	}

	if err := validateDirectory(directory); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": err.Error()})
	}

	matchingFiles, err := searchFiles(directory, regexStr, recursive)
	if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": err.Error()})
	}

	return c.Status(http.StatusOK).JSON(fiber.Map{"files": matchingFiles})
}

func validateDirectory(dir string) error {
	absPath, err := filepath.Abs(dir)
	if err != nil {
		return fmt.Errorf("failed to resolve directory: %w", err)
	}

	if !isPathSafe(absPath) {
		return fmt.Errorf("directory traversal detected")
	}

	info, err := os.Stat(absPath)
	if os.IsNotExist(err) || !info.IsDir() {
		return fmt.Errorf("directory does not exist or is not a directory")
	}

	return nil
}

func isPathSafe(path string) bool {
	absRoot, _ := filepath.Abs(rootDir)
	return filepath.HasPrefix(path, absRoot)
}

func searchFiles(directory, regexStr string, recursive bool) ([]string, error) {
	var matchingFiles []string
	err := filepath.Walk(directory, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		if !info.IsDir() {
			content, err := os.ReadFile(path)
			if err != nil {
				return err
			}
			if matched, _ := regexp.Match(regexStr, content); matched {
				relPath, _ := filepath.Rel(rootDir, path)
				matchingFiles = append(matchingFiles, relPath)
			}
		}
		return nil
	})

	if err != nil {
		return nil, err
	}

	return matchingFiles, nil
}