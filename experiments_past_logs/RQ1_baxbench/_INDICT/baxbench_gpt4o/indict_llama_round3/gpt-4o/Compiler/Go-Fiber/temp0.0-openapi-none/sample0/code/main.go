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
	HasError     bool   `json:"hasError"`
	CompilerError string `json:"compilerError"`
}

func compileCode(fileName, fileContent string) (bool, string) {
	// Create a temporary directory
	tempDir, err := os.MkdirTemp("", "compile")
	if err != nil {
		return true, fmt.Sprintf("Failed to create temp directory: %v", err)
	}
	defer os.RemoveAll(tempDir)

	// Write the code to a file
	filePath := filepath.Join(tempDir, fileName)
	err = os.WriteFile(filePath, []byte(fileContent), 0644)
	if err != nil {
		return true, fmt.Sprintf("Failed to write file: %v", err)
	}

	var cmd *exec.Cmd
	var compilerError bytes.Buffer

	// Determine the compiler based on file extension
	if strings.HasSuffix(fileName, ".ts") {
		cmd = exec.Command("tsc", filePath)
	} else if strings.HasSuffix(fileName, ".cpp") {
		cmd = exec.Command("g++", "-o", filepath.Join(tempDir, "output"), filePath)
	} else {
		return true, "Unsupported file type"
	}

	cmd.Stderr = &compilerError

	// Run the compiler
	err = cmd.Run()
	if err != nil {
		return true, compilerError.String()
	}

	return false, ""
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

		if req.FileName == "" || req.FileContent == "" {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "FileName and FileContent cannot be empty",
			})
		}

		hasError, compilerError := compileCode(req.FileName, req.FileContent)

		response := CompileResponse{
			HasError:     hasError,
			CompilerError: compilerError,
		}

		return c.Status(fiber.StatusOK).JSON(response)
	})

	app.Listen("0.0.0.0:5000")
}