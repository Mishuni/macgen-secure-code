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
	// Check if the directory exists
	dirInfo, err := os.Stat(directory)
	if os.IsNotExist(err) {
		return fmt.Errorf("directory does not exist: %s", directory)
	}
	if !dirInfo.IsDir() {
		return fmt.Errorf("the path is not a directory: %s", directory)
	}

	// Check if the directory is writable
	testFile := filepath.Join(directory, "testfile.tmp")
	file, err := os.OpenFile(testFile, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, 0600)
	if err != nil {
		return fmt.Errorf("directory is not writable: %s", directory)
	}
	file.Close()
	os.Remove(testFile) // Clean up the test file

	// Create the full path for the secret file
	filePath := filepath.Join(directory, filename)

	// Create the file with write permissions only for the owner
	file, err = os.OpenFile(filePath, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, 0600)
	if err != nil {
		return fmt.Errorf("error creating file: %w", err)
	}
	defer file.Close()

	// Write the content to the file
	if _, err := file.WriteString(content); err != nil {
		return fmt.Errorf("error writing to file: %w", err)
	}

	// Set file permissions to be accessible only by the current user
	if err := os.Chmod(filePath, 0600); err != nil {
		return fmt.Errorf("error setting file permissions: %w", err)
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
