
package main

import (
	"io/ioutil"
	"os"
	"path/filepath"
	"strings"
)

// readFileFromDir reads the content of a file from a specified directory.
// If any error occurs during the file reading process, it returns an empty string.
func readFileFromDir(filename, dirPath string) string {
	// Validate inputs to prevent directory traversal attacks
	if strings.Contains(filename, "..") || strings.Contains(dirPath, "..") {
		return ""
	}

	// Construct the full file path
	fullPath := filepath.Join(dirPath, filename)

	// Clean the path to prevent directory traversal
	cleanPath := filepath.Clean(fullPath)

	// Check if the cleaned path starts with the directory path to ensure it's within the directory
	if !strings.HasPrefix(cleanPath, filepath.Clean(dirPath)+string(os.PathSeparator)) {
		return ""
	}

	// Check if the file exists and is not a directory
	fileInfo, err := os.Stat(cleanPath)
	if err != nil || fileInfo.IsDir() {
		return ""
	}

	// Check for file size to prevent memory exhaustion
	if fileInfo.Size() > 1<<20 { // Limit to 1 MB for example
		return ""
	}

	// Read the file content
	content, err := ioutil.ReadFile(cleanPath)
	if err != nil {
		return ""
	}

	return string(content)
}