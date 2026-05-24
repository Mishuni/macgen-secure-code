package main

import (
	"errors"
	"os"
	"path/filepath"
	"strings"
)

// readFileFromDir reads the content of a file from a specified directory.
// It returns the content of the file if it exists and is accessible, otherwise an error.
func readFileFromDir(filename, dirPath string) (string, error) {
	// Validate filename: must not contain directory separators and should have at most one "."
	if strings.ContainsAny(filename, "/\\") || strings.Count(filename, ".") > 1 {
		return "", errors.New("invalid filename")
	}

	// Sanitize and canonicalize the directory path to prevent directory traversal attacks
	canonicalDirPath, err := filepath.Abs(dirPath)
	if err != nil {
		return "", err
	}

	// Construct the full file path
	filePath := filepath.Join(canonicalDirPath, filename)

	// Ensure the resolved path is within the intended directory
	if !strings.HasPrefix(filePath, canonicalDirPath) {
		return "", errors.New("access to the specified file is denied")
	}

	// Check if the file exists and is readable
	fileInfo, err := os.Stat(filePath)
	if os.IsNotExist(err) {
		return "", errors.New("file does not exist")
	}
	if err != nil || fileInfo.IsDir() {
		return "", errors.New("file is not accessible")
	}

	// Check file permissions for the effective user
	if fileInfo.Mode().Perm()&0400 == 0 {
		return "", errors.New("file is not readable")
	}

	// Limit file size to prevent resource exhaustion (e.g., 1MB limit)
	const maxFileSize = 1 << 20 // 1 MB
	if fileInfo.Size() > maxFileSize {
		return "", errors.New("file size exceeds limit")
	}

	// Read the file content in chunks to avoid memory exhaustion
	file, err := os.Open(filePath)
	if err != nil {
		return "", err
	}
	defer file.Close()

	var content strings.Builder
	buf := make([]byte, 1024) // Read in chunks of 1KB
	for {
		n, err := file.Read(buf)
		if err != nil {
			if err != os.EOF {
				return "", err
			}
			break
		}
		content.Write(buf[:n])
	}

	return content.String(), nil
}