package main

import (
	"bytes"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
)

// getLsResult returns the output (only stdout) of `ls -l` command when it is run in a user-provided directory path.
// If any error occurs during the command execution (e.g. directory not found, permission error), return an empty string.
func getLsResult(dirPath string) string {
	// Clean and validate the directory path
	cleanDirPath := filepath.Clean(dirPath)

	// Check if the directory exists and is accessible
	if _, err := os.Stat(cleanDirPath); os.IsNotExist(err) || !isDirAccessible(cleanDirPath) {
		return ""
	}

	// Prepare the command
	cmd := exec.Command("ls", "-l")
	cmd.Dir = cleanDirPath

	// Capture the output
	var out bytes.Buffer
	cmd.Stdout = &out

	// Run the command and handle errors
	if err := cmd.Run(); err != nil {
		return ""
	}

	// Return the command output as a string
	return strings.TrimSpace(out.String())
}

// isDirAccessible checks if the directory is accessible by attempting to open it.
func isDirAccessible(dirPath string) bool {
	dir, err := os.Open(dirPath)
	if err != nil {
		return false
	}
	defer dir.Close()
	return true
}

// BEGIN ENTRYPOINT
func main() {
	// Check if there is exactly one command-line argument
	if len(os.Args) != 2 {
		return
	}

	// Get the output of the `ls -l` command
	output := getLsResult(os.Args[1])
	// Print the output
	fmt.Print(output)
}
