
package main

import (
	"io/ioutil"
	"os"
	"path/filepath"
)

// readFileFromDir reads the content of a file from a specified directory.
// It returns the file content if the file exists and is accessible, otherwise an empty string.
// The returned string will be freed by the caller.
func readFileFromDir(filename, dirPath string) string {
	// Construct the full file path securely
	fullPath := filepath.Join(dirPath, filename)

	// Resolve the absolute path to prevent directory traversal
	absPath, err := filepath.Abs(fullPath)
	if err != nil {
		return ""
	}

	// Ensure the resolved path is within the intended directory
	if !filepath.HasPrefix(absPath, filepath.Clean(dirPath)) {
		return ""
	}

	// Attempt to read the file content
	content, err := ioutil.ReadFile(absPath)
	if err != nil {
		// Return an empty string if any error occurs
		return ""
	}

	return string(content)
}