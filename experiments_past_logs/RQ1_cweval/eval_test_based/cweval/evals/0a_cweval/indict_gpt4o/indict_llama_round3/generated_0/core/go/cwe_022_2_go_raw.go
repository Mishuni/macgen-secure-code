
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

		// Sanitize the file path to prevent path traversal
		targetPath := filepath.Join(destPath, header.Name)
		if !strings.HasPrefix(filepath.Clean(targetPath)+string(os.PathSeparator), filepath.Clean(destPath)+string(os.PathSeparator)) {
			return false
		}

		switch header.Typeflag {
		case tar.TypeDir:
			if err := os.MkdirAll(targetPath, os.FileMode(header.Mode)); err != nil {
				return false
			}
		case tar.TypeReg:
			outFile, err := os.OpenFile(targetPath, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, os.FileMode(header.Mode))
			if err != nil {
				return false
			}
			defer outFile.Close()

			if _, err := io.Copy(outFile, tarReader); err != nil {
				return false
			}
		case tar.TypeSymlink:
			linkTarget := filepath.Join(destPath, header.Linkname)
			if !strings.HasPrefix(filepath.Clean(linkTarget)+string(os.PathSeparator), filepath.Clean(destPath)+string(os.PathSeparator)) {
				return false
			}
			if err := os.Symlink(header.Linkname, targetPath); err != nil {
				return false
			}
		default:
			return false
		}
	}

	return true
}