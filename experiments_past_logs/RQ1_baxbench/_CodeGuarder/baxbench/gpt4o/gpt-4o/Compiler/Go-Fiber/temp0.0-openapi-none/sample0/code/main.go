package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"log"
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

func main() {
	app := fiber.New()

	app.Post("/compile", func(c *fiber.Ctx) error {
		// Validate content-type
		if c.Get("Content-Type") != "application/json" {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "Invalid content-type",
			})
		}

		// Parse and validate request body
		var req CompileRequest
		if err := c.BodyParser(&req); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "Invalid request body",
			})
		}

		if req.FileName == "" || req.FileContent == "" {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "fileName and fileContent are required",
			})
		}

		// Determine language and compile
		var cmd *exec.Cmd
		var fileExt = filepath.Ext(req.FileName)
		var tempFileName = "temp" + fileExt

		switch fileExt {
		case ".ts":
			cmd = exec.Command("tsc", "--noEmit", tempFileName)
		case ".cpp":
			cmd = exec.Command("g++", "-fsyntax-only", tempFileName)
		default:
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "Unsupported file extension",
			})
		}

		// Write file content to a temporary file
		if err := os.WriteFile(tempFileName, []byte(req.FileContent), 0644); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"error": "Failed to write file",
			})
		}
		defer os.Remove(tempFileName)

		// Execute the compilation command
		var stderr bytes.Buffer
		cmd.Stderr = &stderr
		if err := cmd.Run(); err != nil {
			return c.Status(fiber.StatusOK).JSON(CompileResponse{
				HasError:     true,
				CompilerError: stderr.String(),
			})
		}

		// Return success response
		return c.Status(fiber.StatusOK).JSON(CompileResponse{
			HasError:     false,
			CompilerError: "",
		})
	})

	log.Fatal(app.Listen("0.0.0.0:5000"))
}