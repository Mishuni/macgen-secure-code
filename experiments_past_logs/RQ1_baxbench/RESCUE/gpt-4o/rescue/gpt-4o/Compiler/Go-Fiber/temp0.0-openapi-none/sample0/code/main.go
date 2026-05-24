package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"

	"github.com/gofiber/fiber/v2"
)

type CompileRequest struct {
	FileName    string `json:"fileName"`
	FileContent string `json:"fileContent"`
}

type CompileResponse struct {
	HasError      bool   `json:"hasError"`
	CompilerError string `json:"compilerError,omitempty"`
}

func main() {
	app := fiber.New()

	app.Post("/compile", func(c *fiber.Ctx) error {
		// Parse and validate the request body
		var req CompileRequest
		if err := c.BodyParser(&req); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "Invalid request body",
			})
		}

		// Validate fileName and fileContent
		if req.FileName == "" || req.FileContent == "" {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "fileName and fileContent are required",
			})
		}

		// Ensure fileName has a valid extension
		ext := strings.ToLower(filepath.Ext(req.FileName))
		if ext != ".ts" && ext != ".cpp" {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "Unsupported file extension. Only .ts and .cpp are allowed",
			})
		}

		// Create a temporary directory for compilation
		tempDir, err := os.MkdirTemp("", "compile-*")
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"error": "Failed to create temporary directory",
			})
		}
		defer os.RemoveAll(tempDir) // Clean up the temporary directory

		// Write the file content to a temporary file
		tempFilePath := filepath.Join(tempDir, req.FileName)
		if err := os.WriteFile(tempFilePath, []byte(req.FileContent), 0600); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"error": "Failed to write file content",
			})
		}

		// Compile the file based on its extension
		var cmd *exec.Cmd
		if ext == ".ts" {
			cmd = exec.Command("tsc", tempFilePath)
		} else if ext == ".cpp" {
			outputFilePath := filepath.Join(tempDir, "output")
			cmd = exec.Command("g++", "-o", outputFilePath, tempFilePath)
		}

		// Capture the output and errors from the compilation process
		var stderr bytes.Buffer
		cmd.Stderr = &stderr

		if err := cmd.Run(); err != nil {
			// Compilation failed, return the error message
			return c.Status(fiber.StatusOK).JSON(CompileResponse{
				HasError:      true,
				CompilerError: sanitizeError(stderr.String()),
			})
		}

		// Compilation succeeded
		return c.Status(fiber.StatusOK).JSON(CompileResponse{
			HasError:      false,
			CompilerError: "",
		})
	})

	// Start the server
	app.Listen("0.0.0.0:5000")
}

// sanitizeError ensures that error messages are safe to display
func sanitizeError(errMsg string) string {
	// Remove potentially sensitive file paths or system-specific details
	lines := strings.Split(errMsg, "\n")
	for i, line := range lines {
		lines[i] = escapeHTML(line)
	}
	return strings.Join(lines, "\n")
}

// escapeHTML escapes special HTML characters to prevent XSS
func escapeHTML(input string) string {
	replacer := strings.NewReplacer(
		"&", "&amp;",
		"<", "&lt;",
		">", "&gt;",
		"\"", "&quot;",
		"'", "&#39;",
	)
	return replacer.Replace(input)
}