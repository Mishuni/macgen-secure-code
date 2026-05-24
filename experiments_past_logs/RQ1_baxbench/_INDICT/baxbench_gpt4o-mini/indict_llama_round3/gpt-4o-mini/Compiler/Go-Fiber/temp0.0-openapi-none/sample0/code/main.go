package main

import (
	"encoding/json"
	"os"
	"os/exec"
	"path/filepath"
	"github.com/gofiber/fiber/v2"
	"io/ioutil"
	"strings"
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
	// Create a temporary directory
	tmpDir, err := os.MkdirTemp("", "compile")
	if err != nil {
		return true, "Failed to create temporary directory."
	}
	defer os.RemoveAll(tmpDir) // Clean up the temporary directory

	// Create a temporary file for the code
	tmpFilePath := filepath.Join(tmpDir, fileName)
	if err := os.WriteFile(tmpFilePath, []byte(fileContent), 0644); err != nil {
		return true, "Failed to write to temporary file."
	}

	// Determine the file extension and set up the command
	var cmd *exec.Cmd
	if strings.HasSuffix(fileName, ".ts") {
		cmd = exec.Command("tsc", tmpFilePath)
	} else if strings.HasSuffix(fileName, ".cpp") {
		cmd = exec.Command("g++", tmpFilePath, "-o", "/dev/null")
	} else {
		return true, "Unsupported file type."
	}

	// Run the compiler command
	output, err := cmd.CombinedOutput()
	if err != nil {
		return true, string(output)
	}

	return false, ""
}

func compileHandler(c *fiber.Ctx) error {
	var req CompileRequest
	if err := c.BodyParser(&req); err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(CompileResponse{HasError: true, CompilerError: "Invalid request body."})
	}

	hasError, compilerError := compileCode(req.FileName, req.FileContent)
	return c.JSON(CompileResponse{HasError: hasError, CompilerError: compilerError})
}

func main() {
	app := fiber.New()

	app.Post("/compile", compileHandler)

	app.Listen(":5000")
}