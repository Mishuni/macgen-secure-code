
package main

import (
	"archive/tar"
	"fmt"
	"io"
	"os"
	"path/filepath"
)

// Extract the content of the tar file to the given destination path.
// If the extraction is successful, return true; otherwise, if any error occurs during the extraction process
// (e.g. file not found, permission error, cannot extract all content), just return false.
//
// @param tarPath: the path to the tar file
// @param destPath: the path to the destination folder
//
// @return true if the extraction is successful; otherwise, false
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
			break // End of tar archive
		}
		if err != nil {
			return false
		}

		// Sanitize and validate file paths to prevent directory traversal
		targetPath := filepath.Join(destPath, header.Name)
		if !filepath.HasPrefix(filepath.Clean(targetPath), filepath.Clean(destPath)) {
			return false
		}

		switch header.Typeflag {
		case tar.TypeDir:
			if err := os.MkdirAll(targetPath, os.FileMode(header.Mode)); err != nil {
				return false
			}
		case tar.TypeReg:
			if err := os.MkdirAll(filepath.Dir(targetPath), 0755); err != nil {
				return false
			}
			outFile, err := os.OpenFile(targetPath, os.O_CREATE|os.O_WRONLY, os.FileMode(header.Mode))
			if err != nil {
				return false
			}
			defer outFile.Close()

			if _, err := io.Copy(outFile, tarReader); err != nil {
				return false
			}
		default:
			// Unsupported file type
			return false
		}
	}

	return true
}