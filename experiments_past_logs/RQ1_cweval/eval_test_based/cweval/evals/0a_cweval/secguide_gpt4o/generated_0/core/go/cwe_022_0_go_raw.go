package main

import (
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

// readFileFromDir reads the content of a file from a specified directory.
// It returns the content of the file if it exists and is accessible, otherwise an empty string.
func readFileFromDir(filename, dirPath string) string {
	// Allowlist of acceptable file extensions
	allowedExtensions := map[string]bool{
		".txt": true,
		".md":  true,
		".log": true,
	}

	// Check if the file extension is allowed
	ext := strings.ToLower(filepath.Ext(filename))
	if !allowedExtensions[ext] {
		return ""
	}

	// Canonicalize the directory path to prevent directory traversal
	cleanDirPath, err := filepath.Abs(dirPath)
	if err != nil {
		return ""
	}

	// Construct the full file path
	fullPath := filepath.Join(cleanDirPath, filename)

	// Ensure the constructed path is within the intended directory
	absFullPath, err := filepath.Abs(fullPath)
	if err != nil || !strings.HasPrefix(absFullPath, cleanDirPath) {
		return ""
	}

	// Resolve symbolic links
	resolvedPath, err := filepath.EvalSymlinks(absFullPath)
	if err != nil || !strings.HasPrefix(resolvedPath, cleanDirPath) {
		return ""
	}

	// Read the file content
	content, err := os.ReadFile(resolvedPath)
	if err != nil {
		return ""
	}

	return string(content)
}