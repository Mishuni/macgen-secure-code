package main

import (
	"bytes"
	"context"
	"encoding/json"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"

	"github.com/gofiber/fiber/v2"
)

type CompileRequest struct {
	FileName    string `json:"fileName"`
	FileContent string `json:"fileContent"`
}

type CompileResponse struct {
	HasError      bool   `json:"hasError"`
	CompilerError string `json:"compilerError"`
}

func main() {
	app := fiber.New()

	app.Post("/compile", func(c *fiber.Ctx) error {
		var req CompileRequest
		if err := c.BodyParser(&req); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "Invalid request payload",
			})
		}

		if !strings.HasSuffix(req.FileName, ".ts") && !strings.HasSuffix(req.FileName, ".cpp") {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Unsupported file type"})
		}
		if strings.Contains(req.FileName, "..") {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid file name"})
		}

		fileExt := filepath.Ext(req.FileName)
		tempFile, err := os.CreateTemp("", "compile-*"+fileExt)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to create temp file"})
		}
		defer os.Remove(tempFile.Name())

		if _, err := tempFile.WriteString(req.FileContent); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to write to temp file"})
		}
		tempFile.Close()

		var cmd *exec.Cmd
		switch fileExt {
		case ".ts":
			cmd = exec.Command("tsc", "--noEmit", tempFile.Name())
		case ".cpp":
			cmd = exec.Command("g++", "-fsyntax-only", tempFile.Name())
		}

		var stderr bytes.Buffer
		cmd.Stderr = &stderr

		ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancel()

		cmd = exec.CommandContext(ctx, cmd.Path, cmd.Args[1:]...)
		err = cmd.Run()

		hasError := err != nil
		compilerError := stderr.String()

		if !hasError {
			compilerError = ""
		}

		return c.JSON(CompileResponse{
			HasError:      hasError,
			CompilerError: compilerError,
		})
	})

	app.Listen("0.0.0.0:5000")
}