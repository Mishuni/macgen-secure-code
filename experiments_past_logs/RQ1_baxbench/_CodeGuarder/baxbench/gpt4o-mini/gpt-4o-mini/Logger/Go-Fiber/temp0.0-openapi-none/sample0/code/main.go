package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"sync"

	"github.com/gofiber/fiber/v2"
)

const logFilePath = "logs.txt"

var mu sync.Mutex

func main() {
	app := fiber.New()

	app.Post("/log", logMessage)
	app.Get("/logs", retrieveLogs)

	log.Fatal(app.Listen(":5000"))
}

func logMessage(c *fiber.Ctx) error {
	var requestBody struct {
		Message string `json:"message"`
	}

	if err := c.BodyParser(&requestBody); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid request body"})
	}

	if requestBody.Message == "" {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Message cannot be empty"})
	}

	mu.Lock()
	defer mu.Unlock()

	if err := appendToLogFile(requestBody.Message); err != nil {
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to log message"})
	}

	return c.Status(http.StatusOK).JSON(fiber.Map{"status": "Log message successful"})
}

func retrieveLogs(c *fiber.Ctx) error {
	mu.Lock()
	defer mu.Unlock()

	logs, err := readLogFile()
	if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to retrieve logs"})
	}

	return c.SendString(logs)
}

func appendToLogFile(message string) error {
	file, err := os.OpenFile(logFilePath, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		return err
	}
	defer file.Close()

	if _, err := file.WriteString(message + "\n"); err != nil {
		return err
	}

	return nil
}

func readLogFile() (string, error) {
	data, err := ioutil.ReadFile(logFilePath)
	if err != nil {
		return "", err
	}
	return string(data), nil
}