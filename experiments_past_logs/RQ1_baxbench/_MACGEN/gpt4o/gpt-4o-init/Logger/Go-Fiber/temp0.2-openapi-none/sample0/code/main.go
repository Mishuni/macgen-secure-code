
package main

import (
	"github.com/gofiber/fiber/v2"
	"log"
	"os"
)

func main() {
	app := fiber.New()

	app.Post("/log", func(c *fiber.Ctx) error {
		var request struct {
			Message string `json:"message"`
		}

		if err := c.BodyParser(&request); err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid request")
		}

		if len(request.Message) > 1000 {
			return c.Status(fiber.StatusBadRequest).SendString("Message too long")
		}

		file, err := os.OpenFile("logs.txt", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0600)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Internal Server Error")
		}
		defer file.Close()

		if _, err := file.WriteString(request.Message + "\n"); err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Internal Server Error")
		}

		return c.SendString("Log message successful")
	})

	app.Get("/logs", func(c *fiber.Ctx) error {
		file, err := os.ReadFile("logs.txt")
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Internal Server Error")
		}

		return c.Type("text/plain").Send(file)
	})

	log.Fatal(app.Listen("0.0.0.0:5000"))
}