package main

import (
	"archive/tar"
	"io"
	"os"
	"path/filepath"
	"strings"
)

func extractTarToPath(tarPath string, destPath string) bool {
	if strings.Contains(tarPath, "..") || strings.Contains(destPath, "..") {
		return false
	}

	file, err := os.OpenFile(tarPath, os.O_RDONLY, 0)
	if err != nil {
		return false
	}
	defer file.Close()

	tr := tar.NewReader(file)

	for {
		header, err := tr.Next()
		if err == io.EOF {
			break
		}
		if err != nil {
			return false
		}

		target := filepath.Join(destPath, header.Name)

		// Validate that the target path is within the destination path
		if !strings.HasPrefix(filepath.Clean(target), filepath.Clean(destPath)) {
			return false
		}

		switch header.Typeflag {
		case tar.TypeDir:
			if err := os.MkdirAll(target, 0755); err != nil {
				return false
			}
		case tar.TypeReg:
			if err := os.MkdirAll(filepath.Dir(target), 0755); err != nil {
				return false
			}
			outFile, err := os.OpenFile(target, os.O_CREATE|os.O_WRONLY, 0644)
			if err != nil {
				return false
			}
			if _, err := io.Copy(outFile, tr); err != nil {
				outFile.Close()
				return false
			}
			outFile.Close()
		default:
			return false
		}
	}
	return true
}