package main

import (
	"database/sql"
	"fmt"
	"log"
	"net/http"
	"time"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

type Click struct {
	ID        string    `json:"id"`
	Timestamp time.Time `json:"timestamp"`
}

var db *sql.DB

func initDB() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}

	createTableSQL := `CREATE TABLE IF NOT EXISTS clicks (
		id TEXT PRIMARY KEY,
		timestamp DATETIME
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		log.Fatal(err)
	}
}

func registerClick(c *fiber.Ctx) error {
	click := Click{
		ID:        uuid.NewString(),
		Timestamp: time.Now(),
	}

	_, err := db.Exec("INSERT INTO clicks (id, timestamp) VALUES (?, ?)", click.ID, click.Timestamp)
	if err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid request"})
	}

	return c.Status(http.StatusCreated).JSON(click)
}

func retrieveClicks(c *fiber.Ctx) error {
	date := c.Query("date")
	direction := c.Query("direction")

	if date == "" || direction == "" {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid request"})
	}

	var operator string
	switch direction {
	case "<":
		operator = "<"
	case "<=":
		operator = "<="
	case ">":
		operator = ">"
	case ">=":
		operator = ">="
	default:
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid request"})
	}

	query := fmt.Sprintf("SELECT id, timestamp FROM clicks WHERE timestamp %s ?", operator)
	rows, err := db.Query(query, date)
	if err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid request"})
	}
	defer rows.Close()

	var clicks []Click
	for rows.Next() {
		var click Click
		if err := rows.Scan(&click.ID, &click.Timestamp); err != nil {
			return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Internal server error"})
		}
		clicks = append(clicks, click)
	}

	if len(clicks) == 0 {
		return c.Status(http.StatusNotFound).JSON(fiber.Map{"error": "No clicks found"})
	}

	return c.Status(http.StatusOK).JSON(clicks)
}

func main() {
	initDB()
	defer db.Close()

	app := fiber.New()

	app.Post("/click", registerClick)
	app.Get("/clicks", retrieveClicks)

	log.Fatal(app.Listen(":5000"))
}