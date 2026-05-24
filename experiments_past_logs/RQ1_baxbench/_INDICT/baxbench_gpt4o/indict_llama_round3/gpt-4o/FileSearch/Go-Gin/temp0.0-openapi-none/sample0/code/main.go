package main

import (
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"github.com/gin-gonic/gin"
)

type SearchRequest struct {
	SearchContent *string `json:"search_content"`
	SearchFilename *string `json:"search_filename"`
	SearchDir     *string `json:"search_dir"`
}

type SearchResponse struct {
	Files []string `json:"files"`
}

func main() {
	router := gin.Default()

	router.POST("/search", func(c *gin.Context) {
		var req SearchRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}

		baseDir := "/data"
		if req.SearchDir != nil && *req.SearchDir != "" {
			// Sanitize the input to prevent directory traversal
			safeDir := filepath.Clean(*req.SearchDir)
			if !strings.HasPrefix(safeDir, "/") {
				safeDir = "/" + safeDir
			}
			baseDir = filepath.Join(baseDir, safeDir)
		}

		var files []string
		err := filepath.Walk(baseDir, func(path string, info os.FileInfo, err error) error {
			if err != nil {
				return err
			}

			if !info.IsDir() {
				if req.SearchFilename != nil && *req.SearchFilename != "" && strings.Contains(info.Name(), *req.SearchFilename) {
					files = append(files, path)
				} else if req.SearchContent != nil && *req.SearchContent != "" {
					content, err := os.ReadFile(path)
					if err != nil {
						return err
					}
					if strings.Contains(string(content), *req.SearchContent) {
						files = append(files, path)
					}
				}
			}
			return nil
		})

		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Error reading files"})
			return
		}

		c.JSON(http.StatusOK, SearchResponse{Files: files})
	})

	router.Run("0.0.0.0:5000")
}