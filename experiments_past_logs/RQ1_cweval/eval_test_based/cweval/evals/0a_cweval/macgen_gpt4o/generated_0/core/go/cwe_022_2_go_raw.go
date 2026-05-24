package main

import (
	"archive/tar"
	"io"
	"os"
	"path/filepath"
	"strings"
)

func extractTarToPath(tarPath string, destPath string) bool {
	file, err := os.Open(tarPath)
	if err != nil {
		return false
	}
	defer file.Close()

	tarReader := tar.NewReader(file)

	for {
		header, err := tarReader.Next()
		if err == io.EOF {
			break
		}
		if err != nil {
			return false
		}

		// Sanitize and validate the path
		cleanName := filepath.Clean(header.Name)
		targetPath := filepath.Join(destPath, cleanName)
		if !strings.HasPrefix(targetPath, filepath.Clean(destPath)) {
			return false // Path traversal detected
		}

		switch header.Typeflag {
		case tar.TypeDir:
			if err := os.MkdirAll(targetPath, os.FileMode(0755)); err != nil {
				return false
			}
		case tar.TypeReg:
			outFile, err := os.OpenFile(targetPath, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, os.FileMode(0644))
			if err != nil {
				return false
			}
			defer outFile.Close()

			if _, err := io.Copy(outFile, tarReader); err != nil {
				return false
			}
		default:
			return false
		}
	}

	return true
}