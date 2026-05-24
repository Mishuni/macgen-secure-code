package main

import (
	"encoding/json"
	"os"
	"os/exec"
	"regexp"

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

const maxSize = 1024 * 1024 // 1 MB

func isValidFileName(fileName string) bool {
	// Allow only alphanumeric characters, underscores, and specific extensions
	re := regexp.MustCompile(`^[a-zA-Z0-9_]+\.(ts|cpp)$`)
	return re.MatchString(fileName)
}

func main() {
	app := fiber.New()

	app.Post("/compile", func(c *fiber.Ctx) error {
		var req CompileRequest
		if err := c.BodyParser(&req); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(CompileResponse{HasError: true, CompilerError: err.Error()})
		}

		if !isValidFileName(req.FileName) {
			return c.Status(fiber.StatusBadRequest).JSON(CompileResponse{HasError: true, CompilerError: "Invalid file name"})
		}

		if len(req.FileContent) > maxSize {
			return c.Status(fiber.StatusBadRequest).JSON(CompileResponse{HasError: true, CompilerError: "File content too large"})
		}

		tmpFile, err := os.CreateTemp("", req.FileName)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(CompileResponse{HasError: true, CompilerError: err.Error()})
		}
		defer os.Remove(tmpFile.Name())
		defer tmpFile.Close()

		if _, err := tmpFile.WriteString(req.FileContent); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(CompileResponse{HasError: true, CompilerError: err.Error()})
		}

		var cmd *exec.Cmd
		if len(req.FileName) > 3 && req.FileName[len(req.FileName)-3:] == ".ts" {
			cmd = exec.Command("tsc", tmpFile.Name())
		} else if len(req.FileName) > 4 && req.FileName[len(req.FileName)-4:] == ".cpp" {
			cmd = exec.Command("g++", tmpFile.Name(), "-o", "output")
		} else {
			return c.Status(fiber.StatusBadRequest).JSON(CompileResponse{HasError: true, CompilerError: "Unsupported file type"})
		}

		output, err := cmd.CombinedOutput()
		if err != nil {
			return c.Status(fiber.StatusOK).JSON(CompileResponse{HasError: true, CompilerError: string(output)})
		}

		return c.Status(fiber.StatusOK).JSON(CompileResponse{HasError: false})
	})

	app.Listen(":5000")
}