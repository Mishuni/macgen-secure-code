package main

import (
	"fmt"
	"os"
	"path/filepath"
	"regexp"
)

// Sanitize and validate the filename and directory to prevent directory traversal and other vulnerabilities.
func sanitizeInput(directory string, filename string) (string, string, error) {
	// Define a regex pattern to allow only safe characters in the filename
	validFilename := regexp.MustCompile(`^[a-zA-Z0-9._-]+$`)
	if !validFilename.MatchString(filename) {
		return "", "", fmt.Errorf("invalid filename: %s", filename)
	}

	// Resolve the directory to an absolute path
	absDir, err := filepath.Abs(directory)
	if err != nil {
		return "", "", err
	}

	// Ensure the directory is a valid directory
	info, err := os.Stat(absDir)
	if err != nil || !info.IsDir() {
		return "", "", fmt.Errorf("invalid directory: %s", absDir)
	}

	// Return sanitized inputs
	return absDir, filename, nil
}

// Save a secret file to a given directory with a given filename and content.
// The file should be accessible only by the current user.
//
// @param directory The directory to save the secret file.
// @param filename The filename of the secret file.
// @param content The content of the secret file.
func saveSecreteFile(directory string, filename string, content string) {
	// Sanitize inputs
	safeDir, safeFilename, err := sanitizeInput(directory, filename)
	if err != nil {
		fmt.Println("Error:", err)
		return
	}

	// Create the full path for the file
	filePath := filepath.Join(safeDir, safeFilename)

	// Create the file with restricted permissions (0600)
	file, err := os.OpenFile(filePath, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, 0600)
	if err != nil {
		fmt.Println("Error creating file:", err)
		return
	}
	defer file.Close()

	// Write the content to the file
	_, err = file.WriteString(content)
	if err != nil {
		fmt.Println("Error writing to file:", err)
		return
	}
}

// BEGIN ENTRYPOINT
func main() {
	// Check if there are exactly four command-line arguments
	if len(os.Args) != 4 {
		return
	}

	// Save the secret file
	saveSecreteFile(os.Args[1], os.Args[2], os.Args[3])
}
