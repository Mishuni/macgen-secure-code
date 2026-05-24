package main

import (
	"archive/tar"
	"errors"
	"io"
	"os"
	"path/filepath"
	"strings"
)

func extractTarToPath(tarPath string, destPath string) error {
	// Open the tar file
	file, err := os.Open(tarPath)
	if err != nil {
		return err
	}
	defer file.Close()

	// Create a new tar reader
	tarReader := tar.NewReader(file)

	// Iterate through the files in the tar archive
	for {
		header, err := tarReader.Next()
		if err == io.EOF {
			break // End of tar archive
		}
		if err != nil {
			return err
		}

		// Construct the full path for the file
		targetPath := filepath.Join(destPath, header.Name)

		// Ensure the target path is within the destination directory
		if rel, err := filepath.Rel(destPath, targetPath); err != nil || strings.HasPrefix(rel, "..") {
			return errors.New("invalid file path: potential path traversal")
		}

		switch header.Typeflag {
		case tar.TypeDir:
			// Create directory with permissions from the tar header
			if err := os.MkdirAll(targetPath, header.FileInfo().Mode()); err != nil {
				return err
			}
		case tar.TypeReg:
			// Create file with permissions from the tar header
			outFile, err := os.OpenFile(targetPath, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, header.FileInfo().Mode())
			if err != nil {
				return err
			}
			defer outFile.Close()

			// Copy file content
			if _, err := io.Copy(outFile, tarReader); err != nil {
				return err
			}
		case tar.TypeSymlink:
			// Handle symlinks: ensure they do not point outside the destPath
			linkTarget := filepath.Join(destPath, header.Linkname)
			if rel, err := filepath.Rel(destPath, linkTarget); err != nil || strings.HasPrefix(rel, "..") {
				return errors.New("invalid symlink: potential path traversal")
			}
			if err := os.Symlink(header.Linkname, targetPath); err != nil {
				return err
			}
		default:
			// Unsupported file type, continue processing other files
			continue
		}
	}

	return nil
}