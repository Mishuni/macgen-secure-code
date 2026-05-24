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
	// Ensure the directory exists
	os.MkdirAll(directory, 0700)

	// Create the full path for the file
	filePath := filepath.Join(directory, filename)

	// Create the file with restricted permissions
	file, err := os.OpenFile(filePath, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0600)
	if err != nil {
		return
	}
	defer file.Close()

	// Write the content to the file
	file.WriteString(content)

	// Ensure the file is only accessible by the current user
	syscall.Umask(0077)
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
