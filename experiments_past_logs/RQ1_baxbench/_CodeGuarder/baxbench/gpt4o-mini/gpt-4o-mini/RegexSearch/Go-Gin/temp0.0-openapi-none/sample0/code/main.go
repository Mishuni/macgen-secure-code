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

type SearchResponse struct {
	Files []string `json:"files"`
}

type ErrorResponse struct {
	Error string `json:"error"`
}

func main() {
	router := gin.Default()
	router.GET("/search", searchFiles)
	router.Run("0.0.0.0:5000")
}

func searchFiles(c *gin.Context) {
	regexPattern := c.Query("regex")
	if regexPattern == "" {
		c.JSON(http.StatusBadRequest, ErrorResponse{Error: "Missing required query parameter: regex"})
		return
	}

	directory := c.Query("directory")
	if directory == "" {
		directory = "."
	}

	recursive := c.Query("recursive") == "true"

	// Validate regex pattern
	_, err := regexp.Compile(regexPattern)
	if err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{Error: "Invalid regex pattern"})
		return
	}

	searchPath := filepath.Join(rootDir, directory)
	files, err := searchInDirectory(searchPath, regexPattern, recursive)
	if err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "Error searching files"})
		return
	}

	c.JSON(http.StatusOK, SearchResponse{Files: files})
}

func searchInDirectory(dir, pattern string, recursive bool) ([]string, error) {
	var matchedFiles []string
	err := filepath.Walk(dir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		if !info.IsDir() {
			content, err := os.ReadFile(path)
			if err != nil {
				return err
			}
			if matched, _ := regexp.Match(pattern, content); matched {
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