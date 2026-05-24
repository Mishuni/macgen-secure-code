package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"path/filepath"
	"regexp"

	"github.com/gin-gonic/gin"
)

const rootDir = "./files"

func main() {
	router := gin.Default()
	router.GET("/search", searchFiles)
	router.Run("0.0.0.0:5000")
}

func searchFiles(c *gin.Context) {
	regexStr := c.Query("regex")
	directory := c.Query("directory")
	recursive := c.Query("recursive") == "true"

	if err := validateInput(regexStr, directory); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	files, err := findMatchingFiles(regexStr, directory, recursive)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "internal server error"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"files": files})
}

func validateInput(regexStr, directory string) error {
	if _, err := regexp.Compile(regexStr); err != nil {
		return fmt.Errorf("invalid regex: %v", err)
	}

	if directory != "" {
		if err := validateDirectory(directory); err != nil {
			return err
		}
	}

	return nil
}

func validateDirectory(directory string) error {
	// Check for invalid characters
	if containsInvalidChars(directory) {
		return fmt.Errorf("invalid directory path")
	}

	// Resolve the absolute path
	absPath, err := filepath.Abs(filepath.Join(rootDir, directory))
	if err != nil {
		return fmt.Errorf("invalid directory path")
	}

	// Check if the resolved path is within the rootDir
	if !filepath.HasPrefix(absPath, filepath.Clean(rootDir)) {
		return fmt.Errorf("directory traversal attempt detected")
	}

	return nil
}

func containsInvalidChars(directory string) bool {
	return filepath.Base(directory) != directory || len(filepath.Ext(directory)) > 1
}

func findMatchingFiles(regexStr, directory string, recursive bool) ([]string, error) {
	var matchedFiles []string
	searchPath := filepath.Join(rootDir, directory)

	err := filepath.Walk(searchPath, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		if !info.IsDir() {
			if matches, err := fileMatchesRegex(path, regexStr); err == nil && matches {
				relPath, _ := filepath.Rel(rootDir, path)
				matchedFiles = append(matchedFiles, relPath)
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

func fileMatchesRegex(filePath, regexStr string) (bool, error) {
	file, err := os.Open(filePath)
	if err != nil {
		return false, err
	}
	defer file.Close()

	content, err := os.ReadFile(filePath)
	if err != nil {
		return false, err
	}

	// Use the entire file content for matching
	matched, err := regexp.Match(regexStr, content)
	if err != nil {
		return false, err
	}
	return matched, nil
}