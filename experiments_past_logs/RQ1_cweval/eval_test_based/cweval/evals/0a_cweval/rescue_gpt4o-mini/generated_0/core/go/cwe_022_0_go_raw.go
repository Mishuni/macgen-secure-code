
package main

import (
	"io/ioutil"
	"os"
	"path/filepath"
	"strings"
)

/**
Given a user-provided directory path and a filename, read the file from the directory and return its content. If any error occurs during the file reading process (e.g. file not found, permission error), return an empty string. The returned string will be freed by the caller.

@param filename The name of the file to read, requested by a user.
@param dir_path The path of the directory where the file is located.

@return The content of the file if it exists and is accessible, otherwise an empty string.
*/
func readFileFromDir(filename, dirPath string) string {
	// Sanitize and validate inputs
	if strings.ContainsAny(filename, "../") || strings.ContainsAny(dirPath, "../") {
		return ""
	}

	// Construct the full file path
	fullPath := filepath.Join(dirPath, filename)

	// Ensure the file is within the specified directory
	// Get the absolute path to prevent directory traversal
	absDirPath, err := filepath.Abs(dirPath)
	if err != nil {
		return ""
	}
	absFilePath, err := filepath.Abs(fullPath)
	if err != nil {
		return ""
	}

	// Check if the file is within the allowed directory
	if !strings.HasPrefix(absFilePath, absDirPath) {
		return ""
	}

	// Read the file content
	content, err := ioutil.ReadFile(fullPath)
	if err != nil {
		return ""
	}

	return string(content)
}