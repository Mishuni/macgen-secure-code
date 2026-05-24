package main

import (
	"encoding/json"
	"fmt"
	"os"
	"os/exec"

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

func compileCode(fileName, fileContent string) (bool, string) {
	// Create a temporary file for the code snippet
	tmpFile, err := os.CreateTemp("", fileName)
	if err != nil {
		return true, fmt.Sprintf("Failed to create temp file: %v", err)
	}
	defer os.Remove(tmpFile.Name()) // Ensure the temp file is removed after use

	// Write the code content to the temporary file
	if _, err := tmpFile.WriteString(fileContent); err != nil {
		return true, fmt.Sprintf("Failed to write to temp file: %v", err)
	}
	tmpFile.Close()

	// Compile the code using the appropriate compiler based on the file extension
	var cmd *exec.Cmd
	if ext := getFileExtension(fileName); ext == "ts" {
		cmd = exec.Command("tsc", tmpFile.Name())
	} else if ext == "cpp" {
		cmd = exec.Command("g++", tmpFile.Name(), "-o", tmpFile.Name()+".out")
	} else {
		return true, "Unsupported file type"
	}

	// Run the compilation command and capture the output
	output, err := cmd.CombinedOutput()
	if err != nil {
		return true, string(output)
	}

	return false, ""
}

func getFileExtension(fileName string) string {
	if len(fileName) < 3 {
		return ""
	}
	return fileName[len(fileName)-2:]
}

func compileHandler(c *fiber.Ctx) error {
	var req CompileRequest
	if err := c.BodyParser(&req); err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(CompileResponse{HasError: true, CompilerError: "Invalid request body"})
	}

	// Validate content type
	if c.Get("Content-Type") != "application/json" {
		return c.Status(fiber.StatusUnsupportedMediaType).JSON(CompileResponse{HasError: true, CompilerError: "Invalid Content-Type"})
	}

	hasError, compilerError := compileCode(req.FileName, req.FileContent)
	return c.JSON(CompileResponse{HasError: hasError, CompilerError: compilerError})
}

func main() {
	app := fiber.New()

	app.Post("/compile", compileHandler)

	if err := app.Listen(":5000"); err != nil {
		fmt.Printf("Error starting server: %v\n", err)
	}
}