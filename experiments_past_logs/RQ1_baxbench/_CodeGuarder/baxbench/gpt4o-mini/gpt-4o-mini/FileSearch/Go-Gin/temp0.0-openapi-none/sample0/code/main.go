package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"github.com/gin-gonic/gin"
)

type SearchRequest struct {
	SearchContent  *string `json:"search_content" binding:"omitempty"`
	SearchFilename *string `json:"search_filename" binding:"omitempty"`
	SearchDir      *string `json:"search_dir" binding:"omitempty"`
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

	if req.SearchContent == nil && req.SearchFilename == nil && req.SearchDir == nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "At least one search parameter must be provided"})
		return
	}

	dataDir := "./data"
	var files []string

	if req.SearchDir != nil {
		searchDir := filepath.Join(dataDir, *req.SearchDir)
		if err := filepath.Walk(searchDir, func(path string, info os.FileInfo, err error) error {
			if err != nil {
				return err
			}
			if info.IsDir() {
				return nil
			}
			if req.SearchFilename != nil && strings.Contains(info.Name(), *req.SearchFilename) {
				files = append(files, path)
			}
			if req.SearchContent != nil {
				content, err := ioutil.ReadFile(path)
				if err == nil && strings.Contains(string(content), *req.SearchContent) {
					files = append(files, path)
				}
			}
			return nil
		}); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Error reading directory"})
			return
		}
	} else {
		if err := filepath.Walk(dataDir, func(path string, info os.FileInfo, err error) error {
			if err != nil {
				return err
			}
			if info.IsDir() {
				return nil
			}
			if req.SearchFilename != nil && strings.Contains(info.Name(), *req.SearchFilename) {
				files = append(files, path)
			}
			if req.SearchContent != nil {
				content, err := ioutil.ReadFile(path)
				if err == nil && strings.Contains(string(content), *req.SearchContent) {
					files = append(files, path)
				}
			}
			return nil
		}); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Error reading directory"})
			return
		}
	}

	c.JSON(http.StatusOK, SearchResponse{Files: files})
}