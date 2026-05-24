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
	file, err := os.Open(tarPath)
	if err != nil {
		return err
	}
	defer file.Close()

	tarReader := tar.NewReader(file)

	for {
		header, err := tarReader.Next()
		if err != nil {
			if err == io.EOF {
				break
			}
			return err
		}

		if err := validateHeader(header, destPath); err != nil {
			return err
		}

		outputPath := filepath.Join(destPath, header.Name)

		if err := createOutputPath(outputPath, header); err != nil {
			return err
		}

		if header.Typeflag == tar.TypeReg {
			if err := writeFile(outputPath, tarReader); err != nil {
				return err
			}
		}
	}

	return nil
}

func validateHeader(header *tar.Header, destPath string) error {
	if strings.Contains(header.Name, "..") || strings.Contains(header.Name, "/") {
		return errors.New("invalid header: path traversal detected")
	}

	outputPath := filepath.Join(destPath, header.Name)
	if !isValidOutputPath(outputPath) {
		return errors.New("invalid output path")
	}

	return nil
}

func createOutputPath(outputPath string, header *tar.Header) error {
	switch header.Typeflag {
	case tar.TypeDir:
		return os.MkdirAll(outputPath, 0700) // Use more restrictive permissions
	case tar.TypeReg:
		if _, err := os.Stat(outputPath); err == nil {
			return errors.New("file already exists: " + outputPath)
		}
		return nil
	default:
		return errors.New("unsupported header type")
	}
}

func writeFile(outputPath string, tarReader *tar.Reader) error {
	outFile, err := os.Create(outputPath)
	if err != nil {
		return err
	}
	defer outFile.Close()

	_, err = io.Copy(outFile, tarReader)
	if err != nil {
		os.Remove(outputPath) // Clean up the file if copy fails
		return err
	}
	return nil
}

func isValidOutputPath(path string) bool {
	base := filepath.Base(path)
	if strings.Count(base, ".") > 1 || strings.ContainsAny(base, "/\\") {
		return false
	}
	if isSymlink(path) {
		return false
	}
	return true
}

func isSymlink(path string) bool {
	info, err := os.Lstat(path)
	if err != nil {
		return false
	}
	return info.Mode()&os.ModeSymlink != 0
}