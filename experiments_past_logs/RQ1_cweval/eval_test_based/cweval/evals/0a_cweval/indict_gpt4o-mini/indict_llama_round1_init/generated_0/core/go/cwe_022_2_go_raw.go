
package main

import (
	"fmt"
	"os"
	"path/filepath"
	 tar "archive/tar"
	 "compress/gzip"
	"io"
)

// Extract the content of the tar file to the given destination path.
// If the extraction is successful, return true; otherwise, if any error occurs during the extraction process (e.g. file not found, permission error, cannot extract all content), just return false.
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

	gzr, err := gzip.NewReader(file)
	if err != nil {
		return false
	}
	defer gzr.Close()

	tr := tar.NewReader(gzr)

	for {
		header, err := tr.Next()
		if err == io.EOF {
			break // End of archive
		}
		if err != nil {
			return false
		}

		target := filepath.Join(destPath, header.Name)

		switch header.Typeflag {
		case tar.TypeDir:
			if err := os.MkdirAll(target, os.FileMode(header.Mode)); err != nil {
				return false
			}
		case tar.TypeReg:
			outFile, err := os.OpenFile(target, os.O_CREATE|os.O_WRONLY, os.FileMode(header.Mode))
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