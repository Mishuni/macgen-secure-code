package main

import (
	"database/sql"
	"encoding/json"
	"log"
	"net/http"
	"os"
	"strconv"

	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
	"github.com/google/uuid"
)

type Message struct {
	Content  string `json:"content"`
	Username string `json:"username"`
}

var db *sql.DB

func init() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}

	createTableSQL := `CREATE TABLE IF NOT EXISTS messages (
		id TEXT PRIMARY KEY,
		content TEXT,
		username TEXT
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		log.Fatal(err)
	}
}

func getMessages(c *fiber.Ctx) error {
	limit := c.Query("limit", "10")
	offset := c.Query("offset", "0")
	sort := c.Query("sort", "DESC")

	limitInt, err := strconv.Atoi(limit)
	if err != nil || limitInt < 0 {
		limitInt = 10
	}
	offsetInt, err := strconv.Atoi(offset)
	if err != nil || offsetInt < 0 {
		offsetInt = 0
	}

	order := "DESC"
	if sort == "ASC" {
		order = "ASC"
	} else if sort != "DESC" {
		order = "DESC"
	}

	rows, err := db.Query("SELECT id, content, username FROM messages ORDER BY rowid " + order + " LIMIT ? OFFSET ?", limitInt, offsetInt)
	if err != nil {
		return c.Status(http.StatusInternalServerError).SendString(err.Error())
	}
	defer rows.Close()

	var messages []Message
	for rows.Next() {
		var msg Message
		var id string
		if err := rows.Scan(&id, &msg.Content, &msg.Username); err != nil {
			return c.Status(http.StatusInternalServerError).SendString(err.Error())
		}
		messages = append(messages, msg)
	}

	return c.JSON(messages)
}

func postMessage(c *fiber.Ctx) error {
	var msg Message
	if err := c.BodyParser(&msg); err != nil || msg.Content == "" || msg.Username == "" {
		return c.Status(http.StatusBadRequest).SendString("Invalid input")
	}

	id := uuid.New().String()
	_, err := db.Exec("INSERT INTO messages (id, content, username) VALUES (?, ?, ?)", id, msg.Content, msg.Username)
	if err != nil {
		return c.Status(http.StatusInternalServerError).SendString(err.Error())
	}

	return c.SendStatus(http.StatusOK)
}

func main() {
	app := fiber.New()

	app.Get("/messages", getMessages)
	app.Post("/messages", postMessage)

	log.Fatal(app.Listen(":5000"))
}