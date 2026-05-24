
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
	// Ensure the directory exists
	err := os.MkdirAll(directory, 0700) // Create the directory with permissions restricted to the owner
	if err != nil {
		fmt.Printf("Error creating directory: %v\n", err)
		return
	}

	// Construct the full file path
	filePath := filepath.Join(directory, filename)

	// Create a temporary file securely
	tempFile, err := os.CreateTemp(directory, "temp-*")
	if err != nil {
		fmt.Printf("Error creating temporary file: %v\n", err)
		return
	}
	defer func() {
		// Ensure the temporary file is removed in case of any errors
		tempFile.Close()
		os.Remove(tempFile.Name())
	}()

	// Set file permissions to be accessible only by the current user
	err = tempFile.Chmod(0600)
	if err != nil {
		fmt.Printf("Error setting file permissions: %v\n", err)
		return
	}

	// Write the content to the temporary file
	_, err = tempFile.WriteString(content)
	if err != nil {
		fmt.Printf("Error writing to temporary file: %v\n", err)
		return
	}

	// Close the temporary file before renaming
	err = tempFile.Close()
	if err != nil {
		fmt.Printf("Error closing temporary file: %v\n", err)
		return
	}

	// Atomically rename the temporary file to the target file
	err = os.Rename(tempFile.Name(), filePath)
	if err != nil {
		fmt.Printf("Error renaming temporary file: %v\n", err)
		return
	}

	// Ensure the final file has the correct permissions
	err = os.Chmod(filePath, 0600)
	if err != nil {
		fmt.Printf("Error setting final file permissions: %v\n", err)
		return
	}

	fmt.Printf("Secret file saved successfully at: %s\n", filePath)
}