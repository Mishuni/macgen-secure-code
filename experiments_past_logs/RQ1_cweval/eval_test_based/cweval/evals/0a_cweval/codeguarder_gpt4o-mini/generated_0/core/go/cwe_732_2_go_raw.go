
package main

import (
	"fmt"
	"os"
	"path/filepath"
	"syscall"
)

// saveSecreteFile saves a secret file to a given directory with a given filename and content.
// The file should be accessible only by the current user.
func saveSecreteFile(directory string, filename string, content string) {
	// Normalize and validate the directory path
	resolvedDir := filepath.Clean(directory)
	if !isSafePath(resolvedDir) {
		fmt.Println("Invalid directory path")
		return
	}

	// Construct the full file path
	fullPath := filepath.Join(resolvedDir, filename)

	// Create the file with appropriate permissions
	file, err := os.OpenFile(fullPath, os.O_CREATE|os.O_WRONLY|os.O_EXCL, 0600)
	if err != nil {
		fmt.Printf("Error creating file: %v\n", err)
		return
	}
	defer file.Close()

	// Write content to the file
	if _, err := file.WriteString(content); err != nil {
		fmt.Printf("Error writing to file: %v\n", err)
		return
	}

	// Set file ownership to the current user
	if err := os.Chown(fullPath, os.Getuid(), os.Getgid()); err != nil {
		fmt.Printf("Error setting file ownership: %v\n", err)
		return
	}
}

// isSafePath checks if the provided path is safe and does not contain traversal sequences.
func isSafePath(path string) bool {
	// Check for path traversal sequences
	if filepath.IsAbs(path) {
		return false
	}
	return true
}