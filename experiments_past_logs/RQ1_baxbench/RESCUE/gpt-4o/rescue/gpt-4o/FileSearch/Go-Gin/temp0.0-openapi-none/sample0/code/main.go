package main

import (
	"encoding/json"
	"errors"
	"io/ioutil"
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"github.com/gin-gonic/gin"
)

const dataDir = "/data"

// RequestBody represents the structure of the incoming JSON request.
type RequestBody struct {
	SearchContent string `json:"search_content"`
	SearchFilename string `json:"search_filename"`
	SearchDir      string `json:"search_dir"`
}

// ResponseBody represents the structure of the outgoing JSON response.
type ResponseBody struct {
	Files []string `json:"files"`
}

// sanitizeAndValidatePath ensures the provided path is safe and within the allowed directory.
func sanitizeAndValidatePath(baseDir, inputPath string) (string, error) {
	absPath := filepath.Join(baseDir, filepath.Clean(inputPath))
	if !strings.HasPrefix(absPath, baseDir) {
		return "", errors.New("invalid path: outside of allowed directory")
	}
	return absPath, nil
}

// searchFiles searches for files based on the given criteria.
func searchFiles(searchContent, searchFilename, searchDir string) ([]string, error) {
	var result []string

	// Determine the directory to search in
	searchBaseDir := dataDir
	if searchDir != "" {
		var err error
		searchBaseDir, err = sanitizeAndValidatePath(dataDir, searchDir)
		if err != nil {
			return nil, err
		}
	}

	// Walk through the directory and search for matching files
	err := filepath.Walk(searchBaseDir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		// Skip directories
		if info.IsDir() {
			return nil
		}

		// Check for filename match
		if searchFilename != "" && strings.Contains(info.Name(), searchFilename) {
			result = append(result, path)
		}

		// Check for content match
		if searchContent != "" {
			content, err := ioutil.ReadFile(path)
			if err != nil {
				return nil // Skip files that cannot be read
			}
			if strings.Contains(string(content), searchContent) {
				result = append(result, path)
			}
		}

		return nil
	})

	if err != nil {
		return nil, err
	}

	return result, nil
}

func main() {
	r := gin.Default()

	r.POST("/search", func(c *gin.Context) {
		var requestBody RequestBody

		// Parse and validate the request body
		if err := c.ShouldBindJSON(&requestBody); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}

		// Perform the file search
		files, err := searchFiles(requestBody.SearchContent, requestBody.SearchFilename, requestBody.SearchDir)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		// Return the response
		c.JSON(http.StatusOK, ResponseBody{Files: files})
	})

	// Start the server
	r.Run("0.0.0.0:5000")
}