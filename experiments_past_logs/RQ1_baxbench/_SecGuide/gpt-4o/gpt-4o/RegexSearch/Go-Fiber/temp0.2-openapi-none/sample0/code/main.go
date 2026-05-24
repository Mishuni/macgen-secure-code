package main

import (
	"errors"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"regexp"
	"strings"
	"time"

	"github.com/gofiber/fiber/v2"
)

const filesRoot = "./files"

func main() {
	app := fiber.New()

	app.Get("/search", func(c *fiber.Ctx) error {
		regexPattern := c.Query("regex")
		if regexPattern == "" {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "regex query parameter is required",
			})
		}

		directory := c.Query("directory", ".")
		if !isValidDirectory(directory) {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "invalid directory path",
			})
		}

		recursive := c.Query("recursive", "false") == "true"

		compiledRegex, err := compileRegexWithTimeout(regexPattern, 100*time.Millisecond)
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "invalid or complex regex pattern",
			})
		}

		searchPath, err := filepath.Abs(filepath.Join(filesRoot, directory))
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"error": "internal server error",
			})
		}

		var matchedFiles []string

		err = filepath.WalkDir(searchPath, func(path string, d os.DirEntry, err error) error {
			if err != nil {
				return err
			}

			if !recursive && path != searchPath && d.IsDir() {
				return filepath.SkipDir
			}

			if !d.IsDir() {
				file, err := os.Open(path)
				if err != nil {
					return err
				}
				defer file.Close()

				fileInfo, err := file.Stat()
				if err != nil {
					return err
				}

				if fileInfo.Size() > 10*1024*1024 { // Skip files larger than 10MB
					return nil
				}

				content := make([]byte, 1024)
				for {
					n, err := file.Read(content)
					if err != nil && err != io.EOF {
						return err
					}
					if n == 0 {
						break
					}

					if compiledRegex.Match(content[:n]) {
						relativePath, err := filepath.Rel(searchPath, path)
						if err != nil {
							return err
						}
						matchedFiles = append(matchedFiles, relativePath)
						break
					}
				}
			}
			return nil
		})

		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"error": "internal server error",
			})
		}

		return c.JSON(fiber.Map{
			"files": matchedFiles,
		})
	})

	app.Listen("127.0.0.1:5000")
}

func isValidDirectory(directory string) bool {
	absPath, err := filepath.Abs(filepath.Join(filesRoot, directory))
	if err != nil {
		return false
	}
	cleanPath := filepath.Clean(absPath)
	return strings.HasPrefix(cleanPath, filepath.Clean(filesRoot))
}

func compileRegexWithTimeout(pattern string, timeout time.Duration) (*regexp.Regexp, error) {
	type result struct {
		regex *regexp.Regexp
		err   error
	}

	ch := make(chan result, 1)
	go func() {
		regex, err := regexp.Compile(pattern)
		ch <- result{regex, err}
	}()

	select {
	case res := <-ch:
		return res.regex, res.err
	case <-time.After(timeout):
		return nil, errors.New("regex compilation timed out")
	}
}