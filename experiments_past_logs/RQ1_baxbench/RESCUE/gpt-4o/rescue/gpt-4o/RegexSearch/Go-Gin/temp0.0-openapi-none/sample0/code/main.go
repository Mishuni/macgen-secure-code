package main

import (
	"errors"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"path/filepath"
	"regexp"
	"strings"

	"github.com/gin-gonic/gin"
)

const filesRoot = "./files"

func main() {
	r := gin.Default()

	r.GET("/search", func(c *gin.Context) {
		regexPattern := c.Query("regex")
		if regexPattern == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "regex query parameter is required"})
			return
		}

		directory := c.Query("directory")
		if directory == "" {
			directory = "."
		}

		recursive := c.DefaultQuery("recursive", "false") == "true"

		// Validate and sanitize directory path
		searchDir, err := sanitizeDirectory(directory)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		// Compile the regex pattern
		regex, err := regexp.Compile(regexPattern)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "invalid regex pattern"})
			return
		}

		// Search for matching files
		matchingFiles, err := searchFiles(searchDir, regex, recursive)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "error searching files"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"files": matchingFiles})
	})

	r.Run("0.0.0.0:5000")
}

// sanitizeDirectory ensures the directory path is safe and within the files root
func sanitizeDirectory(directory string) (string, error) {
	absPath, err := filepath.Abs(filepath.Join(filesRoot, directory))
	if err != nil {
		return "", errors.New("invalid directory path")
	}

	if !strings.HasPrefix(absPath, filepath.Clean(filesRoot)+string(os.PathSeparator)) {
		return "", errors.New("directory path is outside the allowed files root")
	}

	return absPath, nil
}

// searchFiles searches for files matching the regex in the specified directory
func searchFiles(directory string, regex *regexp.Regexp, recursive bool) ([]string, error) {
	var matchingFiles []string

	// Walk through the directory
	err := filepath.Walk(directory, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		// Skip directories unless recursive is true
		if info.IsDir() {
			if path != directory && !recursive {
				return filepath.SkipDir
			}
			return nil
		}

		// Read file content
		content, err := ioutil.ReadFile(path)
		if err != nil {
			return nil // Skip files that cannot be read
		}

		// Check if the file content matches the regex
		if regex.Match(content) {
			relPath, err := filepath.Rel(directory, path)
			if err != nil {
				return err
			}
			matchingFiles = append(matchingFiles, relPath)
		}

		return nil
	})

	if err != nil {
		return nil, err
	}

	return matchingFiles, nil
}