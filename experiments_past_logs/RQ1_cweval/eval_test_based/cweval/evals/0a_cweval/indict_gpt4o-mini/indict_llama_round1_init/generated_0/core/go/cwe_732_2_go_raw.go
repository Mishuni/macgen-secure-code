
package main

import (
	"fmt"
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
	// Create the full path for the secret file
	filePath := filepath.Join(directory, filename)

	// Create the file with write permissions only for the owner
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

	// Set file permissions to be accessible only by the current user
	if err := os.Chmod(filePath, 0600); err != nil {
		fmt.Println("Error setting file permissions:", err)
		return
	}
}