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
	SearchContent  *string `json:"search_content"`
	SearchFilename *string `json:"search_filename"`
	SearchDir      *string `json:"search_dir"`
}

type SearchResponse struct {
	Files []string `json:"files"`
}

const dataDir = "/data"

func main() {
	router := gin.Default()
	router.POST("/search", searchFiles)
	router.Run("0.0.0.0:5000")
}

func searchFiles(c *gin.Context) {
	var req SearchRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	searchDir := dataDir
	if req.SearchDir != nil {
		// Sanitize and validate the search directory
		relativePath := filepath.Clean(*req.SearchDir)
		if !strings.HasPrefix(relativePath, "/") {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid directory"})
			return
		}
		searchDir = filepath.Join(dataDir, relativePath)
	}

	files, err := os.ReadDir(searchDir)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Unable to read directory"})
		return
	}

	var matchedFiles []string
	for _, file := range files {
		if file.IsDir() {
			continue
		}
		filePath := filepath.Join(searchDir, file.Name())
		if req.SearchFilename != nil && *req.SearchFilename != "" {
			if strings.Contains(file.Name(), *req.SearchFilename) {
				matchedFiles = append(matchedFiles, filePath)
			}
		} else if req.SearchContent != nil && *req.SearchContent != "" {
			content, err := os.ReadFile(filePath)
			if err == nil && strings.Contains(string(content), *req.SearchContent) {
				matchedFiles = append(matchedFiles, filePath)
			}
		} else {
			matchedFiles = append(matchedFiles, filePath)
		}
	}

	c.JSON(http.StatusOK, SearchResponse{Files: matchedFiles})
}