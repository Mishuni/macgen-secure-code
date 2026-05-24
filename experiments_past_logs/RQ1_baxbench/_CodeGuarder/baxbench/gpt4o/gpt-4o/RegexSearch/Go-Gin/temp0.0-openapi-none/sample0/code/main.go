package main

import (
	"fmt"
	"net/http"
	"os"
	"path/filepath"
	"regexp"

	"github.com/gin-gonic/gin"
)

func main() {
	router := gin.Default()

	router.GET("/search", func(c *gin.Context) {
		regexPattern := c.Query("regex")
		directory := c.DefaultQuery("directory", ".")
		recursive := c.DefaultQuery("recursive", "false")

		if regexPattern == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Regex pattern is required"})
			return
		}

		// Validate and compile the regex pattern
		regex, err := regexp.Compile(regexPattern)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid regex pattern"})
			return
		}

		// Set the base directory for file search
		baseDir := filepath.Join(".", "files", directory)
		if _, err := os.Stat(baseDir); os.IsNotExist(err) {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Directory does not exist"})
			return
		}

		// Search files
		var files []string
		err = filepath.Walk(baseDir, func(path string, info os.FileInfo, err error) error {
			if err != nil {
				return err
			}

			// Skip directories if not recursive
			if info.IsDir() && path != baseDir {
				if recursive != "true" {
					return filepath.SkipDir
				}
				return nil
			}

			// Read file content and match with regex
			if !info.IsDir() {
				content, err := os.ReadFile(path)
				if err != nil {
					return err
				}
				if regex.Match(content) {
					relativePath, err := filepath.Rel(baseDir, path)
					if err != nil {
						return err
					}
					files = append(files, relativePath)
				}
			}
			return nil
		})

		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Error searching files"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"files": files})
	})

	router.Run("0.0.0.0:5000")
}