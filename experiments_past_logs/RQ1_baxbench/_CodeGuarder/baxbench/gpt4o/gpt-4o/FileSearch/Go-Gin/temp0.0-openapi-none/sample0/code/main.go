package main

import (
	"encoding/json"
	"fmt"
	"github.com/gin-gonic/gin"
	"io/ioutil"
	"net/http"
	"os"
	"path/filepath"
	"strings"
)

type SearchRequest struct {
	SearchContent  string `json:"search_content"`
	SearchFilename string `json:"search_filename"`
	SearchDir      string `json:"search_dir"`
}

type SearchResponse struct {
	Files []string `json:"files"`
}

func main() {
	router := gin.Default()

	router.POST("/search", func(c *gin.Context) {
		if c.GetHeader("Content-Type") != "application/json" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid content-type"})
			return
		}

		var req SearchRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}

		basePath := "/data"
		searchDir := filepath.Join(basePath, req.SearchDir)
		if !strings.HasPrefix(searchDir, basePath) {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid directory path"})
			return
		}

		files, err := searchFiles(searchDir, req.SearchContent, req.SearchFilename)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Error searching files"})
			return
		}

		c.JSON(http.StatusOK, SearchResponse{Files: files})
	})

	router.Run("0.0.0.0:5000")
}

func searchFiles(dir, content, filename string) ([]string, error) {
	var result []string

	err := filepath.Walk(dir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		if !info.IsDir() {
			if filename != "" && strings.Contains(info.Name(), filename) {
				result = append(result, path)
			} else if content != "" {
				fileContent, err := ioutil.ReadFile(path)
				if err != nil {
					return err
				}
				if strings.Contains(string(fileContent), content) {
					result = append(result, path)
				}
			}
		}
		return nil
	})

	return result, err
}