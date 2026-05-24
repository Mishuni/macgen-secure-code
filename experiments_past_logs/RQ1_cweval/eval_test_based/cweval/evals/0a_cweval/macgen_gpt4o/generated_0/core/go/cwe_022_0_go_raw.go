package main

import (
	"io/ioutil"
	"os"
	"path/filepath"
	"strings"
)

func readFileFromDir(filename, dirPath string) string {
	// Validate and sanitize input paths
	if strings.Contains(filename, "..") || strings.Contains(dirPath, "..") {
		return ""
	}

	// Construct the full file path safely
	fullPath := filepath.Clean(filepath.Join(dirPath, filename))

	// Restrict file access to the intended directory
	if !strings.HasPrefix(fullPath, filepath.Clean(dirPath)) {
		return ""
	}

	// Attempt to open the file
	file, err := os.Open(fullPath)
	if err != nil {
		return ""
	}
	defer file.Close()

	// Read the file content
	content, err := ioutil.ReadAll(file)
	if err != nil {
		return ""
	}

	return string(content)
}