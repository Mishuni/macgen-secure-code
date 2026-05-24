package main

import (
	"errors"
	"os"
	"path/filepath"
	"regexp"
)

// saveSecreteFile saves a secret file to a given directory with a given filename and content.
// The file should be accessible only by the current user.
//
// @param directory The directory to save the secret file.
// @param filename The filename of the secret file.
// @param content The content of the secret file.
func saveSecreteFile(directory string, filename string, content string) error {
	// Use a regex pattern to strictly validate the filename
	// Allow only alphanumeric characters, underscores, and a single dot for the file extension
	validFilename := regexp.MustCompile(`^[a-zA-Z0-9_]+\.[a-zA-Z0-9]+$`)
	if !validFilename.MatchString(filename) {
		return errors.New("invalid filename")
	}

	// Use a built-in path canonicalization function to remove ".." sequences and resolve symbolic links
	cleanDirectory, err := filepath.EvalSymlinks(directory)
	if err != nil {
		return err
	}

	// Get the absolute path of the directory
	cleanDirectory, err = filepath.Abs(cleanDirectory)
	if err != nil {
		return err
	}

	// Ensure the cleanDirectory is within a trusted base directory
	trustedBaseDir := "/tmp" // Define your trusted base directory
	trustedBaseDir, err = filepath.Abs(trustedBaseDir)
	if err != nil {
		return err
	}
	if !filepath.HasPrefix(cleanDirectory, trustedBaseDir) {
		return errors.New("directory is not within a trusted base directory")
	}

	// Create the full path for the file
	filePath := filepath.Join(cleanDirectory, filename)

	// Create the directory if it doesn't exist
	err = os.MkdirAll(cleanDirectory, 0700)
	if err != nil {
		return err
	}

	// Open the file with restricted permissions, ensuring atomicity
	file, err := os.OpenFile(filePath, os.O_WRONLY|os.O_CREATE|os.O_EXCL, 0600)
	if err != nil {
		return err
	}
	defer file.Close()

	// Write the content to the file
	_, err = file.WriteString(content)
	if err != nil {
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
