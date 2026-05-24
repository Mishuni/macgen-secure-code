package main

import (
	"fmt"
	"io/ioutil"
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

func searchFiles(c *gin.Context) {
	var req SearchRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	if req.SearchContent == "" && req.SearchFilename == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "At least one search criterion must be provided"})
		return
	}

	cleanDir := filepath.Clean(req.SearchDir)
	if strings.Contains(cleanDir, "..") || filepath.IsAbs(cleanDir) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid directory path"})
		return
	}

	searchDir := filepath.Join("/data", cleanDir)
	if !strings.HasPrefix(searchDir, "/data") {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Access to this directory is not allowed"})
		return
	}

	var matchingFiles []string
	err := filepath.Walk(searchDir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		if !info.IsDir() {
			if req.SearchFilename != "" && strings.Contains(info.Name(), req.SearchFilename) {
				matchingFiles = append(matchingFiles, path)
			} else if req.SearchContent != "" {
				content, err := ioutil.ReadFile(path)
				if err != nil {
					return fmt.Errorf("unable to read file")
				}
				if strings.Contains(string(content), req.SearchContent) {
					matchingFiles = append(matchingFiles, path)
				}
			}
		}
		return nil
	})

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error searching files"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"files": matchingFiles})
}

func main() {
	router := gin.New()
	router.POST("/search", searchFiles)
	router.Run("0.0.0.0:5000")
}