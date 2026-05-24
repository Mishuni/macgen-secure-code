package main

import (
	"database/sql"
	"log"
	"os"
	"strconv"

	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
)

type Message struct {
	Content  string `json:"content"`
	Username string `json:"username"`
}

func main() {
	app := fiber.New()

	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS messages (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		content TEXT NOT NULL,
		username TEXT NOT NULL,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	)`)
	if err != nil {
		log.Fatal(err)
	}

	app.Get("/messages", func(c *fiber.Ctx) error {
		limit := c.Query("limit", "10")
		offset := c.Query("offset", "0")
		sort := c.Query("sort", "DESC")

		limitInt, err := strconv.Atoi(limit)
		if err != nil || limitInt < 0 {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid limit")
		}

		offsetInt, err := strconv.Atoi(offset)
		if err != nil || offsetInt < 0 {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid offset")
		}

		if sort != "ASC" && sort != "DESC" {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid sort")
		}

		rows, err := db.Query(`SELECT content, username FROM messages ORDER BY created_at `+sort+` LIMIT ? OFFSET ?`, limitInt, offsetInt)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Database query error")
		}
		defer rows.Close()

		messages := []Message{}
		for rows.Next() {
			var msg Message
			if err := rows.Scan(&msg.Content, &msg.Username); err != nil {
				return c.Status(fiber.StatusInternalServerError).SendString("Error scanning row")
			}
			messages = append(messages, msg)
		}

		return c.JSON(messages)
	})

	app.Post("/messages", func(c *fiber.Ctx) error {
		var msg Message
		if err := c.BodyParser(&msg); err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid input")
		}

		if msg.Content == "" || msg.Username == "" {
			return c.Status(fiber.StatusBadRequest).SendString("Content and Username are required")
		}

		_, err := db.Exec(`INSERT INTO messages (content, username) VALUES (?, ?)`, msg.Content, msg.Username)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Database insert error")
		}

		return c.SendStatus(fiber.StatusOK)
	})

	log.Fatal(app.Listen("0.0.0.0:5000"))
}