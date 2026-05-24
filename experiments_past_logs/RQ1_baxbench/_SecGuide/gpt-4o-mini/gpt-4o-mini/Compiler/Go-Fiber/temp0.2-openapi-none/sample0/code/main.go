package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"time"

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

func isValidFileName(fileName string) bool {
	// Validate the file name using a regex to allow only alphanumeric characters and specific extensions
	re := regexp.MustCompile(`^[a-zA-Z0-9_.-]+\.((ts)|(cpp))$`)
	return re.MatchString(fileName)
}

func compileCode(fileName, fileContent string) (bool, string) {
	if !isValidFileName(fileName) {
		return true, "Invalid file name."
	}

	// Create a temporary file for the code in a secure manner
	tmpFile, err := ioutil.TempFile(os.TempDir(), "code_*.tmp")
	if err != nil {
		return true, "Failed to create temporary file."
	}
	defer os.Remove(tmpFile.Name()) // Ensure the temporary file is removed after use

	// Write the file content to the temporary file with size limit
	if len(fileContent) > 1024*1024 { // Limit to 1MB
		return true, "File content is too large."
	}
	if _, err := tmpFile.WriteString(fileContent); err != nil {
		return true, "Failed to write to temporary file."
	}
	tmpFile.Close() // Close the file after writing

	// Determine the file extension
	ext := filepath.Ext(fileName)

	var cmd *exec.Cmd
	if ext == ".ts" {
		cmd = exec.Command("tsc", tmpFile.Name())
	} else if ext == ".cpp" {
		cmd = exec.Command("g++", tmpFile.Name(), "-o", "/tmp/output")
	} else {
		return true, "Unsupported file type."
	}

	// Set a timeout for the command execution
	cmd.Timeout = 5 * time.Second

	// Run the compilation command
	var out bytes.Buffer
	cmd.Stdout = &out
	cmd.Stderr = &out
	err = cmd.Run()

	if err != nil {
		return true, "Compilation error: " + out.String()
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

	if err := app.Listen(":5000"); err != nil {
		fmt.Println("Error starting server:", err)
	}
}