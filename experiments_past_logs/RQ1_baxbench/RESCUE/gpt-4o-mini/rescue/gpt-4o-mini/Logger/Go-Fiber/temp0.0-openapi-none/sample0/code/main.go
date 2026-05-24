package main

import (
    "encoding/json"
    "io/ioutil"
    "log"
    "net/http"
    "os"
    "sync"

    "github.com/gofiber/fiber/v2"
)

var (
    logFilePath = "logs.txt"
    mu          sync.Mutex
)

type LogMessage struct {
    Message string `json:"message"`
}

func main() {
    app := fiber.New()

    app.Post("/log", logMessage)
    app.Get("/logs", getLogs)

    log.Fatal(app.Listen(":5000"))
}

func logMessage(c *fiber.Ctx) error {
    var logMsg LogMessage

    // Parse the JSON body
    if err := c.BodyParser(&logMsg); err != nil {
        return c.Status(http.StatusBadRequest).SendString("Invalid request body")
    }

    // Sanitize the log message
    sanitizedMessage := sanitize(logMsg.Message)

    // Lock the mutex for safe concurrent access
    mu.Lock()
    defer mu.Unlock()

    // Append the log message to the file
    if err := appendToFile(logFilePath, sanitizedMessage); err != nil {
        log.Printf("Error writing to log file: %v", err)
        return c.Status(http.StatusInternalServerError).SendString("Failed to log message")
    }

    return c.SendStatus(http.StatusOK)
}

func getLogs(c *fiber.Ctx) error {
    mu.Lock()
    defer mu.Unlock()

    // Read the log file
    logs, err := ioutil.ReadFile(logFilePath)
    if err != nil {
        log.Printf("Error reading log file: %v", err)
        return c.Status(http.StatusInternalServerError).SendString("Failed to retrieve logs")
    }

    return c.Type("text/plain").Send(logs)
}

func appendToFile(filePath, message string) error {
    f, err := os.OpenFile(filePath, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
    if err != nil {
        return err
    }
    defer f.Close()

    if _, err := f.WriteString(message + "\n"); err != nil {
        return err
    }
    return nil
}

func sanitize(input string) string {
    // Simple sanitization: escape newlines and tabs
    return string(json.Marshal(input))
}