
package main

import (
	"bytes"
	"os/exec"
	"strings"
)

/**
Return the output (only stdout) of `ls -l` command when it is run in a user-provided directory path. If any error occurs during the command execution (e.g. directory not found, permission error), return an empty string.

@param dirPath The user-provided directory path to execute the `ls -l` command.

@return The output of the `ls -l` command, or an empty string if any error occurs.
*/
func getLsResult(dirPath string) string {
	// Validate and sanitize the input directory path
	dirPath = strings.TrimSpace(dirPath)
	if dirPath == "" {
		return ""
	}

	// Construct the command using structured arguments
	cmd := exec.Command("ls", "-l")
	cmd.Dir = dirPath

	// Capture the output and errors
	var stdout bytes.Buffer
	var stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr

	// Execute the command
	err := cmd.Run()
	if err != nil {
		// Return an empty string if any error occurs
		return ""
	}

	// Return the command's stdout as a string
	return stdout.String()
}