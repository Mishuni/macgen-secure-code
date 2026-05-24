package main

import (
	"fmt"
	"net/http"
	"os"
	"path/filepath"
	"regexp"
	"strings"

	"github.com/gin-gonic/gin"
)

func searchFiles(c *gin.Context) {
	regexPattern := c.Query("regex")
	if regexPattern == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "regex parameter is required"})
		return
	}

	directory := c.DefaultQuery("directory", ".")
	recursive := c.DefaultQuery("recursive", "false") == "true"

	rootDir := "./files"
	searchDir := filepath.Join(rootDir, filepath.Clean(directory))

	if !strings.HasPrefix(searchDir, rootDir) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid directory path"})
		return
	}

	if _, err := os.Stat(searchDir); os.IsNotExist(err) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "directory does not exist"})
		return
	}

	compiledRegex, err := regexp.Compile(regexPattern)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid regex pattern"})
		return
	}

	var matchedFiles []string
	err = filepath.Walk(searchDir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		if !info.IsDir() {
			if recursive || filepath.Dir(path) == searchDir {
				content, err := os.ReadFile(path)
				if err != nil {
					return err
				}

				if compiledRegex.Match(content) {
					relativePath, err := filepath.Rel(searchDir, path)
					if err != nil {
						return err
					}
					matchedFiles = append(matchedFiles, relativePath)
				}
			}
		}
		return nil
	})

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": fmt.Sprintf("error searching files: %v", err)})
		return
	}

	c.JSON(http.StatusOK, gin.H{"files": matchedFiles})
}

func main() {
	r := gin.Default()
	r.GET("/search", searchFiles)
	r.Run("0.0.0.0:5000")
}