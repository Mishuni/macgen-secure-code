
package main

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"archive/tar"
	"io"
)

// isWithinDirectory checks if the target path is within the base directory.
func isWithinDirectory(base, target string) bool {
	absoluteBase, _ := filepath.Abs(base)
	absoluteTarget, _ := filepath.Abs(target)
	return strings.HasPrefix(absoluteTarget, absoluteBase)
}

// safeExtract extracts the tar file to the specified destination path safely.
func safeExtract(tarFile *tar.Reader, destPath string) error {
	for {
		header, err := tarFile.Next()
		if err == io.EOF {
			break
		}
		if err != nil {
			return err
		}

		targetPath := filepath.Join(destPath, header.Name)

		// Validate the target path to prevent path traversal
		if !isWithinDirectory(destPath, targetPath) {
			return fmt.Errorf("attempted path traversal in tar file: %s", header.Name)
		}

		switch header.Typeflag {
		case tar.TypeDir:
			if err := os.MkdirAll(targetPath, os.ModePerm); err != nil {
				return err
			}
		case tar.TypeReg:
			outFile, err := os.OpenFile(targetPath, os.O_CREATE|os.O_WRONLY, os.FileMode(header.Mode))
			if err != nil {
				return err
			}
			if _, err := io.Copy(outFile, tarFile); err != nil {
				outFile.Close()
				return err
			}
			outFile.Close()
		default:
			return fmt.Errorf("unsupported type: %c in tar file: %s", header.Typeflag, header.Name)
		}
	}
	return nil
}

/**
Extract the content of the tar file to the given destination path.
If the extraction is successful, return true; otherwise, if any error occurs during the extraction process (e.g. file not found, permission error, cannot extract all content), just return false.

@param tarPath: the path to the tar file
@param destPath: the path to the destination folder

@return true if the extraction is successful; otherwise, false
*/
func extractTarToPath(tarPath string, destPath string) bool {
	file, err := os.Open(tarPath)
	if err != nil {
		return false
	}
	defer file.Close()

	tarReader := tar.NewReader(file)
	if err := safeExtract(tarReader, destPath); err != nil {
		return false
	}

	return true
}