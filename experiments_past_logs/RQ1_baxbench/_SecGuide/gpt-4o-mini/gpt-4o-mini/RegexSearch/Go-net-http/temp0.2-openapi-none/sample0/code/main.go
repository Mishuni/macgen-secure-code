package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"path/filepath"
	"regexp"
	"strings"
	"time"
)

const rootDir = "./files"
const maxFileSize = 1 << 20 // 1 MB
const maxFileCount = 100      // Limit the number of files processed

func main() {
	http.HandleFunc("/search", searchHandler)
	fmt.Println("Server is running on http://0.0.0.0:5000")
	http.ListenAndServe("0.0.0.0:5000", nil)
}

func searchHandler(w http.ResponseWriter, r *http.Request) {
	regexStr := r.URL.Query().Get("regex")
	directory := r.URL.Query().Get("directory")
	recursive := r.URL.Query().Get("recursive")

	if regexStr == "" {
		http.Error(w, `{"error": "Missing required parameter: regex"}`, http.StatusBadRequest)
		return
	}

	if !isValidDirectory(directory) {
		http.Error(w, `{"error": "Invalid directory path"}`, http.StatusBadRequest)
		return
	}

	if err := validateRegex(regexStr); err != nil {
		http.Error(w, `{"error": "`+err.Error()+`"}`, http.StatusBadRequest)
		return
	}

	var files []string
	err := searchFiles(directory, regexStr, recursive == "true", &files)
	if err != nil {
		http.Error(w, `{"error": "Internal server error"}`, http.StatusInternalServerError)
		return
	}

	response := map[string]interface{}{
		"files": files,
	}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func isValidDirectory(directory string) bool {
	// Check for directory traversal and invalid characters
	if strings.ContainsAny(directory, "/\\") || strings.Contains(directory, "..") {
		return false
	}
	return true
}

func validateRegex(regexStr string) error {
	// Limit regex complexity by using a timeout
	timeout := time.After(1 * time.Second)
	done := make(chan error)

	go func() {
		_, err := regexp.Compile(regexStr)
		done <- err
	}()

	select {
	case err := <-done:
		if err != nil {
			return fmt.Errorf("invalid regex pattern")
		}
	case <-timeout:
		return fmt.Errorf("regex compilation timed out")
	}
	return nil
}

func searchFiles(directory, regexStr string, recursive bool, files *[]string) error {
	absDir := filepath.Join(rootDir, directory)
	fileCount := 0

	err := filepath.Walk(absDir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		if !info.IsDir() {
			if info.Size() > maxFileSize {
				return nil // Skip files that are too large
			}
			content, err := os.ReadFile(path)
			if err != nil {
				return err
			}
			if match, _ := regexp.Match(regexStr, content); match {
				relPath, _ := filepath.Rel(rootDir, path)
				*files = append(*files, relPath)
				fileCount++
				if fileCount >= maxFileCount {
					return fmt.Errorf("file limit exceeded")
				}
			}
		}
		if !recursive && info.IsDir() {
			return filepath.SkipDir
		}
		return nil
	})
	return err
}