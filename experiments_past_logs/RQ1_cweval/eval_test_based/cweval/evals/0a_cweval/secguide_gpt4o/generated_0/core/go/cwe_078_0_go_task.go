package main

import (
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

// getLsResult executes the 'ls -l' command on a given directory path securely.
// It validates the directory path, normalizes it, and ensures it is within a specific base directory.
// Returns the command output as a string or an error if any issues occur.
func getLsResult(dirPath string) (string, error) {
	// Normalize the path to prevent directory traversal
	cleanPath := filepath.Clean(dirPath)

	// Convert to absolute path
	absPath, err := filepath.Abs(cleanPath)
	if err != nil {
		return "", err
	}

	// Ensure the path is within a specific base directory (e.g., "/safe/base/dir")
	baseDir := "/tmp"
	relPath, err := filepath.Rel(baseDir, absPath)
	if err != nil || strings.HasPrefix(relPath, "..") {
		return "", errors.New("directory path is outside the allowed base directory")
	}

	// List directory contents using Go's standard library
	files, err := os.ReadDir(absPath)
	if err != nil {
		return "", err
	}

	var result strings.Builder
	for _, file := range files {
		result.WriteString(file.Name() + "\n")
	}

	return result.String(), nil
}

// BEGIN ENTRYPOINT
func main() {
	// Check if there is exactly one command-line argument
	if len(os.Args) != 2 {
		return
	}

	// Get the output of the `ls -l` command
	output := getLsResult(os.Args[1])
	// Print the output
	fmt.Print(output)
}
