package main

import (
	"fmt"
	"os"
	"path/filepath"
)

// Save a secret file to a given directory with a given filename and content.
// The file should be accessible only by the current user.
//
// @param directory The directory to save the secret file.
// @param filename The filename of the secret file.
// @param content The content of the secret file.
func saveSecreteFile(directory string, filename string, content string) error {
	// Resolve the absolute path of the directory
	absDir, err := filepath.Abs(directory)
	if err != nil {
		return fmt.Errorf("failed to resolve directory path: %v", err)
	}

	// Ensure the directory exists and has the correct permissions
	if err := os.MkdirAll(absDir, 0700); err != nil {
		return fmt.Errorf("failed to create directory: %v", err)
	}

	// Construct the full file path
	filePath := filepath.Join(absDir, filename)

	// Open the file with exclusive creation to prevent race conditions
	file, err := os.OpenFile(filePath, os.O_WRONLY|os.O_CREATE|os.O_EXCL, 0600)
	if err != nil {
		return fmt.Errorf("failed to open file: %v", err)
	}
	defer file.Close()

	// Write the content to the file
	if _, err := file.WriteString(content); err != nil {
		return fmt.Errorf("failed to write to file: %v", err)
	}

	// Ensure the file is owned by the current user and has the correct permissions
	if err := os.Chown(filePath, os.Getuid(), os.Getgid()); err != nil {
		return fmt.Errorf("failed to set file ownership: %v", err)
	}

	return nil
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
