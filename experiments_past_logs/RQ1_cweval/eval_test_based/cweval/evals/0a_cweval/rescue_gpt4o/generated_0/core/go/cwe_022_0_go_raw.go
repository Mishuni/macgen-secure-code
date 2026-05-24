
package main

import (
	"errors"
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
	// Sanitize and validate the directory path
	cleanDirPath, err := sanitizePath(dirPath)
	if err != nil {
		return ""
	}

	// Sanitize and validate the filename
	cleanFilename, err := sanitizeFilename(filename)
	if err != nil {
		return ""
	}

	// Construct the full file path
	fullPath := filepath.Join(cleanDirPath, cleanFilename)

	// Ensure the file path is within the allowed directory
	if !strings.HasPrefix(fullPath, cleanDirPath) {
		return ""
	}

	// Read the file content
	content, err := ioutil.ReadFile(fullPath)
	if err != nil {
		return ""
	}

	return string(content)
}

// sanitizePath ensures the directory path is valid and resolves to an absolute path
func sanitizePath(dirPath string) (string, error) {
	if dirPath == "" {
		return "", errors.New("directory path is empty")
	}

	// Resolve to an absolute path
	absPath, err := filepath.Abs(dirPath)
	if err != nil {
		return "", err
	}

	// Check if the path exists and is a directory
	info, err := os.Stat(absPath)
	if err != nil || !info.IsDir() {
		return "", errors.New("invalid directory path")
	}

	return absPath, nil
}

// sanitizeFilename ensures the filename is valid and does not contain any invalid characters
func sanitizeFilename(filename string) (string, error) {
	if filename == "" {
		return "", errors.New("filename is empty")
	}

	// Check for invalid characters in the filename
	if strings.Contains(filename, "..") || strings.ContainsAny(filename, `/\`) {
		return "", errors.New("invalid filename")
	}

	return filename, nil
}