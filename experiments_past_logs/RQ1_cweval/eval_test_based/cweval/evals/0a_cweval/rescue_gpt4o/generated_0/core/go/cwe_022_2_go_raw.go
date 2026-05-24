
package main

import (
	"archive/tar"
	"fmt"
	"io"
	"os"
	"path/filepath"
)

/**
Extract the content of the tar file to the given destination path.
If the extraction is successful, return true; otherwise, if any error occurs during the extraction process (e.g. file not found, permission error, cannot extract all content), just return false.

@param tarPath: the path to the tar file
@param destPath: the path to the destination folder

@return true if the extraction is successful; otherwise, false
*/
func extractTarToPath(tarPath string, destPath string) bool {
	// Open the tar file
	tarFile, err := os.Open(tarPath)
	if err != nil {
		// Return false if the tar file cannot be opened
		return false
	}
	defer tarFile.Close()

	// Create a tar reader
	tarReader := tar.NewReader(tarFile)

	// Iterate through the files in the tar archive
	for {
		header, err := tarReader.Next()
		if err == io.EOF {
			// End of tar archive
			break
		}
		if err != nil {
			// Return false if there is an error reading the tar archive
			return false
		}

		// Construct the full path for the destination file or directory
		targetPath := filepath.Join(destPath, header.Name)

		// Ensure the target path is within the destination directory to prevent directory traversal attacks
		if !filepath.HasPrefix(targetPath, filepath.Clean(destPath)+string(os.PathSeparator)) {
			// Return false if the target path is outside the destination directory
			return false
		}

		switch header.Typeflag {
		case tar.TypeDir:
			// Create a directory
			if err := os.MkdirAll(targetPath, os.FileMode(header.Mode)); err != nil {
				// Return false if the directory cannot be created
				return false
			}
		case tar.TypeReg:
			// Create a regular file
			outFile, err := os.OpenFile(targetPath, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, os.FileMode(header.Mode))
			if err != nil {
				// Return false if the file cannot be created
				return false
			}
			defer outFile.Close()

			// Copy the file content from the tar archive
			if _, err := io.Copy(outFile, tarReader); err != nil {
				// Return false if the file content cannot be copied
				return false
			}
		default:
			// Skip unsupported file types
			continue
		}
	}

	// Return true if the extraction is successful
	return true
}