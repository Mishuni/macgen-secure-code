package main

import (
	"encoding/json"
	"net/http"
	"os"
	"path/filepath"
	"regexp"

	"github.com/gin-gonic/gin"
)

type SearchResponse struct {
	Files []string `json:"files"`
}

type ErrorResponse struct {
	Error string `json:"error"`
}

func main() {
	r := gin.Default()
	r.GET("/search", searchFiles)
	r.Run("0.0.0.0:5000")
}

func searchFiles(c *gin.Context) {
	regexStr := c.Query("regex")
	directory := c.Query("directory")
	recursive := c.Query("recursive") == "true"

	if regexStr == "" {
		c.JSON(http.StatusBadRequest, ErrorResponse{Error: "regex parameter is required"})
		return
	}

	// Compile the regex
	re, err := regexp.Compile(regexStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{Error: "invalid regex"})
		return
	}

	// Set the root directory
	rootDir := "./files"
	if directory != "" {
		// Validate the directory to prevent directory traversal attacks
		if filepath.IsAbs(directory) || filepath.Clean(directory) != directory {
			c.JSON(http.StatusBadRequest, ErrorResponse{Error: "invalid directory path"})
			return
		}
		rootDir = filepath.Join(rootDir, directory)
	}

	// Search files
	files, err := findMatchingFiles(rootDir, re, recursive)
	if err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "error searching files"})
		return
	}

	c.JSON(http.StatusOK, SearchResponse{Files: files})
}

func findMatchingFiles(dir string, re *regexp.Regexp, recursive bool) ([]string, error) {
	var matchingFiles []string

	err := filepath.Walk(dir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		if !info.IsDir() {
			content, err := os.ReadFile(path)
			if err != nil {
				return err
			}
			if re.Match(content) {
				relPath, _ := filepath.Rel("./files", path)
				matchingFiles = append(matchingFiles, relPath)
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

	return matchingFiles, nil
}