package main

import (
	"database/sql"
	"fmt"
	"log"
	"os"
	"time"

	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
	"github.com/google/uuid"
)

const dbFileName = "db.sqlite3"

func initDB() (*sql.DB, error) {
	db, err := sql.Open("sqlite3", dbFileName)
	if err != nil {
		return nil, err
	}

	createTableQuery := `
	CREATE TABLE IF NOT EXISTS clicks (
		id TEXT PRIMARY KEY,
		timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
	);`
	_, err = db.Exec(createTableQuery)
	if err != nil {
		return nil, err
	}

	return db, nil
}

func registerClick(c *fiber.Ctx) error {
	db, err := initDB()
	if err != nil {
		return c.Status(fiber.StatusInternalServerError).SendString("Database connection error")
	}
	defer db.Close()

	id := uuid.New().String()
	_, err = db.Exec("INSERT INTO clicks (id) VALUES (?)", id)
	if err != nil {
		return c.Status(fiber.StatusInternalServerError).SendString("Failed to register click")
	}

	return c.Status(fiber.StatusCreated).SendString("Click registered successfully")
}

func retrieveClicks(c *fiber.Ctx) error {
	date := c.Query("date")
	direction := c.Query("direction")

	if date == "" || direction == "" {
		return c.Status(fiber.StatusBadRequest).SendString("Missing query parameters")
	}

	if direction != "<" && direction != ">" && direction != "<=" && direction != ">=" {
		return c.Status(fiber.StatusBadRequest).SendString("Invalid direction parameter")
	}

	db, err := initDB()
	if err != nil {
		return c.Status(fiber.StatusInternalServerError).SendString("Database connection error")
	}
	defer db.Close()

	query := fmt.Sprintf("SELECT id, timestamp FROM clicks WHERE timestamp %s ?", direction)
	rows, err := db.Query(query, date)
	if err != nil {
		return c.Status(fiber.StatusInternalServerError).SendString("Failed to retrieve clicks")
	}
	defer rows.Close()

	var clicks []map[string]interface{}
	for rows.Next() {
		var id string
		var timestamp time.Time
		if err := rows.Scan(&id, &timestamp); err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Failed to parse click data")
		}
		clicks = append(clicks, map[string]interface{}{
			"id":        id,
			"timestamp": timestamp,
		})
	}

	if len(clicks) == 0 {
		return c.Status(fiber.StatusNotFound).SendString("No clicks found")
	}

	return c.JSON(clicks)
}

func main() {
	app := fiber.New()

	app.Post("/click", registerClick)
	app.Get("/clicks", retrieveClicks)

	log.Fatal(app.Listen("0.0.0.0:5000"))
}