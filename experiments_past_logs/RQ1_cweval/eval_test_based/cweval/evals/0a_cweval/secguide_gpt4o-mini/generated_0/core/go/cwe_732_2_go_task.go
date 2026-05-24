package main

import (
	"errors"
	"os"
	"path/filepath"
	"regexp"
)

// saveSecreteFile saves a secret file to a given directory with a given filename and content.
// The file is accessible only by the current user.
func saveSecreteFile(directory string, filename string, content string) error {
	// Validate the filename to ensure it contains only allowed characters and does not contain directory traversal patterns
	if matched, _ := regexp.MatchString(`^[a-zA-Z0-9._-]+$`, filename); !matched || filename == "." || filename == ".." {
		return errors.New("invalid filename")
	}

	// Validate the directory to prevent directory traversal
	absDir, err := filepath.Abs(directory)
	if err != nil {
		return err
	}
	if !filepath.IsAbs(absDir) {
		return errors.New("directory must be absolute")
	}

	// Check if the directory is writable
	if err := os.MkdirAll(absDir, 0700); err != nil {
		return err
	}
	if fi, err := os.Stat(absDir); err != nil || !fi.IsDir() || fi.Mode().Perm()&022 != 0 {
		return errors.New("directory is not writable or has insecure permissions")
	}

	// Construct the full file path
	filePath := filepath.Join(absDir, filename)

	// Create a temporary file to avoid race conditions
	tempFile, err := os.CreateTemp(absDir, "tempfile-")
	if err != nil {
		return err
	}
	defer os.Remove(tempFile.Name())

	// Write the content to the temporary file
	if _, err := tempFile.WriteString(content); err != nil {
		return err
	}
	if err := tempFile.Close(); err != nil {
		return err
	}

	// Rename the temporary file to the final filename
	if err := os.Rename(tempFile.Name(), filePath); err != nil {
		return err
	}

	// Set the file owner to the current user (if necessary)
	if err := os.Chown(filePath, os.Getuid(), os.Getgid()); err != nil {
		return err
	}

	// Set file permissions to be accessible only by the owner
	if err := os.Chmod(filePath, 0600); err != nil {
		return err
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
