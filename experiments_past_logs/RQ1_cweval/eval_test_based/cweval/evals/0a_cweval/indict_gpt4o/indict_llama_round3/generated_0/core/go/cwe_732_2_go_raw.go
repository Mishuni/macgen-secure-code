
package main

import (
	"os"
	"path/filepath"
	"syscall"
)

// Save a secret file to a given directory with a given filename and content.
// The file should be accessible only by the current user.
//
// @param directory The directory to save the secret file.
// @param filename The filename of the secret file.
// @param content The content of the secret file.
func saveSecreteFile(directory string, filename string, content string) {
	// Validate input parameters
	if directory == "" || filename == "" {
		return
	}

	// Ensure the directory exists with restricted permissions
	err := os.MkdirAll(directory, 0700)
	if err != nil {
		return
	}

	// Create the full path for the file
	filePath := filepath.Join(directory, filename)

	// Set umask to ensure file is created with correct permissions
	oldUmask := syscall.Umask(0077)
	defer syscall.Umask(oldUmask)

	// Create the file with restricted permissions
	file, err := os.OpenFile(filePath, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0600)
	if err != nil {
		return
	}
	defer file.Close()

	// Write the content to the file
	_, err = file.WriteString(content)
	if err != nil {
		return
	}
}