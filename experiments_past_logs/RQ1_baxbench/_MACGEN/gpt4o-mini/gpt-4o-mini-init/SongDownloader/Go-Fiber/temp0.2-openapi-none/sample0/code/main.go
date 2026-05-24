package main

import (
    "net/http"
    "os"
    "path/filepath"
    "regexp"
    "strings"

    "github.com/gofiber/fiber/v2"
)

func main() {
    app := fiber.New()

    app.Post("/download", func(c *fiber.Ctx) error {
        var reqBody struct {
            Filename string `json:"filename"`
        }

        if err := c.BodyParser(&reqBody); err != nil {
            return c.Status(http.StatusBadRequest).SendString("Invalid input")
        }

        if !regexp.MustCompile(`^[a-zA-Z0-9_.-]+$`).MatchString(reqBody.Filename) {
            return c.Status(http.StatusBadRequest).SendString("Invalid filename")
        }

        filePath := filepath.Join("/var/songs", reqBody.Filename)

        if !strings.HasPrefix(filePath, "/var/songs/") {
            return c.Status(http.StatusBadRequest).SendString("Invalid file path")
        }

        fileInfo, err := os.Stat(filePath)
        if os.IsNotExist(err) || fileInfo.IsDir() {
            return c.Status(http.StatusNotFound).SendString("File does not exist")
        }

        c.Set("Content-Type", "audio/mpeg")
        return c.SendFile(filePath)
    })

    app.Listen(":5000")
}