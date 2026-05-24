package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
)

type Message struct {
	Content  string `json:"content"`
	Username string `json:"username"`
}

func main() {
	app := fiber.New()

	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS messages (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		content TEXT NOT NULL,
		username TEXT NOT NULL
	)`)
	if err != nil {
		log.Fatal(err)
	}

	app.Get("/messages", func(c *fiber.Ctx) error {
		limit := c.QueryInt("limit", 10)
		offset := c.QueryInt("offset", 0)
		sort := c.Query("sort", "DESC")

		if sort != "ASC" && sort != "DESC" {
			return c.Status(http.StatusBadRequest).SendString("Invalid sort parameter")
		}

		rows, err := db.Query(fmt.Sprintf("SELECT content, username FROM messages ORDER BY id %s LIMIT ? OFFSET ?", sort), limit, offset)
		if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Error retrieving messages")
		}
		defer rows.Close()

		var messages []Message
		for rows.Next() {
			var msg Message
			if err := rows.Scan(&msg.Content, &msg.Username); err != nil {
				return c.Status(http.StatusInternalServerError).SendString("Error scanning message")
			}
			messages = append(messages, msg)
		}

		return c.JSON(messages)
	})

	app.Post("/messages", func(c *fiber.Ctx) error {
		var msg Message
		if err := c.BodyParser(&msg); err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}

		if len(msg.Content) > 500 || len(msg.Username) > 50 {
			return c.Status(http.StatusBadRequest).SendString("Input exceeds length limits")
		}

		_, err := db.Exec("INSERT INTO messages (content, username) VALUES (?, ?)", msg.Content, msg.Username)
		if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Error inserting message")
		}

		return c.SendStatus(http.StatusOK)
	})

	log.Fatal(app.Listen(":5000"))
}