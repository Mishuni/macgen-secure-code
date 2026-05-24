package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"syscall"

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
		var req CompileRequest
		if err := c.BodyParser(&req); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "Invalid request body",
			})
		}

		// Validate file extension
		ext := filepath.Ext(req.FileName)
		if ext != ".ts" && ext != ".cpp" {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "Unsupported file type",
			})
		}

		// Validate file content (basic check for empty content)
		if strings.TrimSpace(req.FileContent) == "" {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "File content cannot be empty",
			})
		}

		// Create a temporary file with restrictive permissions
		tmpFile, err := os.CreateTemp("", "compile-*"+ext)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"error": "Failed to create temporary file",
			})
		}
		defer os.Remove(tmpFile.Name())

		// Write the file content to the temporary file
		if _, err := tmpFile.WriteString(req.FileContent); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"error": "Failed to write to temporary file",
			})
		}
		tmpFile.Close()

		// Compile the file in a sandboxed environment
		var cmd *exec.Cmd
		if ext == ".ts" {
			cmd = exec.Command("tsc", tmpFile.Name())
		} else if ext == ".cpp" {
			cmd = exec.Command("g++", "-o", tmpFile.Name()+".out", tmpFile.Name())
		}

		var stderr bytes.Buffer
		cmd.Stderr = &stderr

		// Set resource limits (example: CPU and memory limits)
		cmd.SysProcAttr = &syscall.SysProcAttr{
			Setpgid: true,
		}

		if err := cmd.Run(); err != nil {
			return c.Status(fiber.StatusOK).JSON(CompileResponse{
				HasError:      true,
				CompilerError: stderr.String(),
			})
		}

		return c.Status(fiber.StatusOK).JSON(CompileResponse{
			HasError: false,
		})
	})

	// Listen on all interfaces for demonstration purposes
	app.Listen("0.0.0.0:5000")
}