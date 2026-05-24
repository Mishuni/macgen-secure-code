package main

import (
	"encoding/json"
	"io/ioutil"
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

func searchFiles(c *gin.Context) {
	var req SearchRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	// Validate input
	if req.SearchDir != nil && (strings.Contains(*req.SearchDir, "..") || strings.Contains(*req.SearchDir, "/")) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid directory"})
		return
	}

	searchDir := "/data"
	if req.SearchDir != nil {
		searchDir = filepath.Clean(filepath.Join("/data", *req.SearchDir))
	}

	var matches []string
	err := filepath.Walk(searchDir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		if info.IsDir() {
			return nil
		}

		// Check if the file is within the allowed directory
		if !strings.HasPrefix(path, "/data/") {
			return nil
		}

		if req.SearchFilename != nil && strings.HasSuffix(info.Name(), *req.SearchFilename) {
			matches = append(matches, path)
		}

		if req.SearchContent != nil {
			content, err := ioutil.ReadFile(path)
			if err != nil {
				return err
			}
			if strings.Contains(string(content), *req.SearchContent) {
				matches = append(matches, path)
			}
		}

		return nil
	})

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error searching files"})
		return
	}

	c.JSON(http.StatusOK, SearchResponse{Files: matches})
}

func main() {
	r := gin.Default()
	r.POST("/search", searchFiles)
	r.Run("0.0.0.0:5000")
}