package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"github.com/gin-gonic/gin"
)

type SearchRequest struct {
	SearchContent string `json:"search_content"`
	SearchFilename string `json:"search_filename"`
	SearchDir string `json:"search_dir"`
}

type SearchResponse struct {
	Files []string `json:"files"`
}

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

	// Validate input
	if !isValidInput(req.SearchContent) || !isValidInput(req.SearchFilename) || !isValidInput(req.SearchDir) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	baseDir := "/data"
	searchDir := filepath.Join(baseDir, filepath.Clean(req.SearchDir))
	absBaseDir, err := filepath.Abs(baseDir)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Server error"})
		return
	}
	absSearchDir, err := filepath.Abs(searchDir)
	if err != nil || !strings.HasPrefix(absSearchDir, absBaseDir) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid directory"})
		return
	}

	var matchedFiles []string
	err = filepath.Walk(searchDir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			// Log the error and continue
			fmt.Printf("Error accessing path: %v\n", err)
			return nil
		}

		if !info.IsDir() {
			if req.SearchFilename != "" && strings.Contains(info.Name(), req.SearchFilename) {
				matchedFiles = append(matchedFiles, path)
			} else if req.SearchContent != "" {
				// Check file size before reading
				if info.Size() > 10*1024*1024 { // 10 MB limit
					fmt.Printf("Skipping large file\n")
					return nil
				}
				content, err := os.ReadFile(path)
				if err != nil {
					// Log the error and continue
					fmt.Printf("Error reading file: %v\n", err)
					return nil
				}
				if strings.Contains(string(content), req.SearchContent) {
					matchedFiles = append(matchedFiles, path)
				}
			}
		}
		return nil
	})

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error searching files"})
		return
	}

	c.JSON(http.StatusOK, SearchResponse{Files: matchedFiles})
}

func isValidInput(input string) bool {
	// Basic validation to check for potentially harmful input
	if strings.Contains(input, "..") || strings.ContainsAny(input, "<>:\"|?*\x00") {
		return false
	}
	return true
}