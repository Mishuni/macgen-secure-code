package main

import (
	"encoding/json"
	"net/http"
	"os"
	"path/filepath"
	"regexp"

	"github.com/gin-gonic/gin"
)

const filesRoot = "./files"

func main() {
	router := gin.Default()
	router.GET("/search", searchFiles)
	router.Run("0.0.0.0:5000")
}

func searchFiles(c *gin.Context) {
	regexStr := c.Query("regex")
	directory := c.Query("directory")
	recursive := c.Query("recursive")

	// Validate regex
	re, err := regexp.Compile(regexStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid regex pattern"})
		return
	}

	// Sanitize and validate directory input
	if directory != "" {
		if !isValidDirectory(directory) {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid directory"})
			return
		}
	}

	var files []string
	err = filepath.Walk(filepath.Join(filesRoot, directory), func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		if !info.IsDir() {
			content, readErr := os.ReadFile(path)
			if readErr != nil {
				return readErr
			}
			if re.Match(content) {
				relativePath, _ := filepath.Rel(filesRoot, path)
				files = append(files, relativePath)
			}
		}
		if !recursive && info.IsDir() && path != filepath.Join(filesRoot, directory) {
			return filepath.SkipDir
		}
		return nil
	})

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"files": files})
}

func isValidDirectory(directory string) bool {
	// Ensure the directory is relative and does not contain any path traversal characters
	absPath, err := filepath.Abs(filepath.Join(filesRoot, directory))
	if err != nil {
		return false
	}
	return filepath.HasPrefix(absPath, filepath.Join(filesRoot, "")) // Check if it is within the files root
}