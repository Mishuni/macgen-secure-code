package main

import (
	"os/exec"
	"path/filepath"
)

func getLsResult(dirPath string) string {
	// Sanitize the directory path
	safeDirPath := filepath.Clean(dirPath)

	cmd := exec.Command("ls", "-l", safeDirPath)
	output, err := cmd.Output()
	if err != nil {
		return ""
	}
	return string(output)
}