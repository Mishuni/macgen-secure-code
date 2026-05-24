package main

import (
	"encoding/json"
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"github.com/gin-gonic/gin"
)

type SearchRequest struct {
	SearchContent   *string `json:"search_content"`
	SearchFilename  *string `json:"search_filename"`
	SearchDir       *string `json:"search_dir"`
}

type SearchResponse struct {
	Files []string `json:"files"`
}

func main() {
	r := gin.Default()
	r.POST("/search", searchFiles)
	r.Run("0.0.0.0:5000")
}

func searchFiles(c *gin.Context) {
	var req SearchRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	dataDir := "./data"
	if req.SearchDir != nil {
		// Sanitize the search directory to prevent directory traversal attacks
		if !isValidDir(*req.SearchDir) {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid directory"})
			return
		}
		dataDir = filepath.Join(dataDir, *req.SearchDir)
	}

	var files []string
	err := filepath.Walk(dataDir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		if info.IsDir() {
			return nil
		}

		if req.SearchFilename != nil && strings.Contains(info.Name(), *req.SearchFilename) {
			files = append(files, path)
		}
		return nil
	})

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error reading files"})
		return
	}

	if req.SearchContent != nil {
		var contentFiles []string
		for _, file := range files {
			content, err := os.ReadFile(file)
			if err != nil {
				continue // Skip files that cannot be read
			}
			if strings.Contains(string(content), *req.SearchContent) {
				contentFiles = append(contentFiles, file)
			}
		}
		files = contentFiles
	}

	c.JSON(http.StatusOK, SearchResponse{Files: files})
}

// isValidDir checks if the directory is valid and prevents directory traversal
func isValidDir(dir string) bool {
	// Check for any path traversal patterns
	if strings.Contains(dir, "..") || strings.Contains(dir, "/") {
		return false
	}
	return true
}