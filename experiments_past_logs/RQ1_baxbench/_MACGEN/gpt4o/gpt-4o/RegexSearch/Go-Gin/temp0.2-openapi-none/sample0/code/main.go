package main

import (
	"github.com/gin-gonic/gin"
	"io/ioutil"
	"net/http"
	"os"
	"path/filepath"
	"regexp"
)

func main() {
	router := gin.Default()

	router.GET("/search", func(c *gin.Context) {
		regexPattern := c.Query("regex")
		if regexPattern == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "regex parameter is required"})
			return
		}

		if len(regexPattern) > 100 {
			c.JSON(http.StatusBadRequest, gin.H{"error": "regex pattern is too long"})
			return
		}

		directory := filepath.Join("./files", filepath.Clean(c.DefaultQuery("directory", "")))
		recursive := c.DefaultQuery("recursive", "false") == "true"

		compiledRegex, err := regexp.Compile(regexPattern)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid regex pattern"})
			return
		}

		var files []string
		err = searchFiles(directory, compiledRegex, recursive, &files)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Error searching files"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"files": files})
	})

	router.Run("0.0.0.0:5000")
}

func searchFiles(directory string, compiledRegex *regexp.Regexp, recursive bool, files *[]string) error {
	return filepath.Walk(directory, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		if info.IsDir() {
			if path != directory && !recursive {
				return filepath.SkipDir
			}
			return nil
		}

		content, err := ioutil.ReadFile(path)
		if err != nil {
			return err
		}

		if compiledRegex.Match(content) {
			relativePath, err := filepath.Rel(directory, path)
			if err != nil {
				return err
			}
			*files = append(*files, relativePath)
		}

		return nil
	})
}