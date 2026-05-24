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
	// Create a temporary file for the code
	tmpFile, err := os.CreateTemp("", fileName)
	if err != nil {
		return true, fmt.Sprintf("Error creating temp file: %v", err)
	}
	defer os.Remove(tmpFile.Name()) // Clean up the temp file

	// Write the file content to the temporary file
	if _, err := tmpFile.WriteString(fileContent); err != nil {
		return true, fmt.Sprintf("Error writing to temp file: %v", err)
	}
	tmpFile.Close()

	// Determine the file extension to choose the compiler
	var cmd *exec.Cmd
	if len(fileName) > 3 && fileName[len(fileName)-3:] == ".ts" {
		cmd = exec.Command("tsc", tmpFile.Name())
	} else if len(fileName) > 4 && fileName[len(fileName)-4:] == ".cpp" {
		cmd = exec.Command("g++", tmpFile.Name(), "-o", "/dev/null")
	} else {
		return true, "Unsupported file type. Only .ts and .cpp are allowed."
	}

	// Run the compiler command and capture the output
	output, err := cmd.CombinedOutput()
	if err != nil {
		return true, string(output) // Return the compiler error output
	}

	return false, "" // No error
}

func compileHandler(c *fiber.Ctx) error {
	var req CompileRequest
	if err := c.BodyParser(&req); err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(CompileResponse{HasError: true, CompilerError: "Invalid request body"})
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