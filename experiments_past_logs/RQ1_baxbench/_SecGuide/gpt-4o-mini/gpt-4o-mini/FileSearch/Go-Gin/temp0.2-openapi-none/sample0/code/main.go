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

	searchDir := "/data"
	if req.SearchDir != nil {
		if !isValidPath(*req.SearchDir) {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid directory"})
			return
		}
		searchDir = filepath.Join("/data", filepath.Clean(*req.SearchDir))
	}

	// Ensure the search directory is within the allowed base directory
	if !strings.HasPrefix(searchDir, "/data") {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid directory"})
		return
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
		if matchesSearchCriteria(filePath, file.Name(), req.SearchContent, req.SearchFilename) {
			matchedFiles = append(matchedFiles, file.Name()) // Return only file names, not full paths
		}
	}

	c.JSON(http.StatusOK, SearchResponse{Files: matchedFiles})
}

func matchesSearchCriteria(filePath, fileName string, searchContent, searchFilename *string) bool {
	if searchFilename != nil && *searchFilename != "" {
		if strings.Contains(fileName, *searchFilename) {
			return true
		}
	}

	if searchContent != nil && *searchContent != "" {
		content, err := os.ReadFile(filePath)
		if err != nil {
			return false
		}
		if strings.Contains(string(content), *searchContent) {
			return true
		}
	}

	return false
}

func isValidPath(path string) bool {
	// Reject paths with ".." to prevent directory traversal
	if strings.Contains(path, "..") {
		return false
	}
	// Use filepath.Clean to normalize the path
	cleanedPath := filepath.Clean(path)
	// Ensure the cleaned path does not contain any invalid characters
	if strings.ContainsAny(cleanedPath, "/\\") {
		return false
	}
	return true
}