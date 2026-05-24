
package main

import (
	"fmt"
	"io/ioutil"
	"os"
	"path/filepath"
	"strings"
)

// readFileFromDir reads the content of a file from a specified directory.
// If any error occurs during the file reading process (e.g. file not found, permission error),
// it returns an empty string. The returned string will be freed by the caller.
//
// @param filename The name of the file to read, requested by a user.
// @param dir_path The path of the directory where the file is located.
//
// @return The content of the file if it exists and is accessible, otherwise an empty string.
func readFileFromDir(filename, dirPath string) string {
	// Validate and resolve the directory path
	resolvedDirPath, err := filepath.Abs(dirPath)
	if err != nil {
		return ""
	}

	// Construct the full file path
	filePath := filepath.Join(resolvedDirPath, filename)

	// Ensure the file path is within the intended directory
	if !strings.HasPrefix(filePath, resolvedDirPath) {
		return ""
	}

	// Read the file content
	content, err := ioutil.ReadFile(filePath)
	if err != nil {
		return ""
	}

	return string(content)
}