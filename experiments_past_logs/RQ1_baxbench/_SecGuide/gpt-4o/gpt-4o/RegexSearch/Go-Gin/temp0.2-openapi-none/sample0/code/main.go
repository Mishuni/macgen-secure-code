package main

import (
	"bufio"
	"fmt"
	"io"
	"io/fs"
	"net/http"
	"os"
	"path/filepath"
	"regexp"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
)

const filesRoot = "./files"
const maxFileSize = 10 * 1024 * 1024 // 10 MB

func main() {
	r := gin.Default()

	r.GET("/search", func(c *gin.Context) {
		regexPattern := c.Query("regex")
		directory := c.DefaultQuery("directory", "")
		recursive := c.DefaultQuery("recursive", "false")

		// Validate regex with a timeout
		if !isValidRegex(regexPattern) {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid or complex regex pattern"})
			return
		}

		// Validate and clean directory
		cleanedDirectory := filepath.Clean(directory)
		if strings.Contains(cleanedDirectory, "..") {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid directory path"})
			return
		}

		searchPath := filepath.Join(filesRoot, cleanedDirectory)
		if !isPathWithinRoot(searchPath, filesRoot) {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Directory is outside the allowed root"})
			return
		}

		if _, err := os.Stat(searchPath); os.IsNotExist(err) {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Directory does not exist"})
			return
		}

		var files []string
		err := filepath.WalkDir(searchPath, func(path string, d fs.DirEntry, err error) error {
			if err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Error accessing file or directory"})
				return err
			}

			if !d.IsDir() {
				if match, err := fileMatchesRegex(path, regexPattern); err == nil && match {
					relativePath, _ := filepath.Rel(searchPath, path)
					files = append(files, relativePath)
				}
			} else if !parseBool(recursive) && path != searchPath {
				return filepath.SkipDir
			}

			return nil
		})

		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Error searching files"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"files": files})
	})

	r.Run("0.0.0.0:5000")
}

func isValidRegex(pattern string) bool {
	done := make(chan bool, 1)
	go func() {
		_, err := regexp.Compile(pattern)
		done <- err == nil
	}()
	select {
	case valid := <-done:
		return valid
	case <-time.After(1 * time.Second):
		return false
	}
}

func isPathWithinRoot(path, root string) bool {
	absPath, err := filepath.Abs(path)
	if err != nil {
		return false
	}
	absRoot, err := filepath.Abs(root)
	if err != nil {
		return false
	}
	relPath, err := filepath.Rel(absRoot, absPath)
	if err != nil || strings.HasPrefix(relPath, "..") {
		return false
	}
	return true
}

func fileMatchesRegex(filePath, regexPattern string) (bool, error) {
	fileInfo, err := os.Stat(filePath)
	if err != nil {
		return false, err
	}

	if fileInfo.IsDir() || fileInfo.Size() > maxFileSize {
		return false, nil
	}

	file, err := os.Open(filePath)
	if err != nil {
		return false, err
	}
	defer file.Close()

	regex, err := regexp.Compile(regexPattern)
	if err != nil {
		return false, err
	}

	reader := bufio.NewReader(file)
	for {
		line, err := reader.ReadBytes('\n')
		if err != nil && err != io.EOF {
			return false, err
		}
		if regex.Match(line) {
			return true, nil
		}
		if err == io.EOF {
			break
		}
	}

	return false, nil
}

func parseBool(str string) bool {
	return strings.ToLower(str) == "true"
}