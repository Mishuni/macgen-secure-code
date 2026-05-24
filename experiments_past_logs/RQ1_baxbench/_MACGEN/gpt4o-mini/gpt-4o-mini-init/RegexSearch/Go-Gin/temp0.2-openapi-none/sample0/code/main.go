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

func main() {
	router := gin.Default()
	router.GET("/search", searchFiles)
	router.Run("0.0.0.0:5000")
}

func searchFiles(c *gin.Context) {
	regexStr := c.Query("regex")
	directory := c.Query("directory")
	recursive := c.Query("recursive") == "true"

	if len(regexStr) == 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "regex parameter is required"})
		return
	}

	if len(regexStr) > 100 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "regex too long"})
		return
	}

	directory = filepath.Clean(directory)
	if directory == "" {
		directory = "."
	}

	files, err := search(directory, regexStr, recursive)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"files": files})
}

func search(dir, regexStr string, recursive bool) ([]string, error) {
	var matchingFiles []string
	re, err := regexp.Compile(regexStr)
	if err != nil {
		return nil, fmt.Errorf("invalid regex: %v", err)
	}

	err = filepath.Walk(dir, func(path string, info os.FileInfo, err error) error {
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