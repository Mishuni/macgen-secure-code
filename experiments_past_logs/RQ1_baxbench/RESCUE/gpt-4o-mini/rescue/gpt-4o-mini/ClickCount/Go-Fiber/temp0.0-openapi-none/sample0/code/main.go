package main

import (
    "database/sql"
    "fmt"
    "log"
    "net/http"
    "os"
    "time"

    "github.com/gofiber/fiber/v2"
    _ "github.com/mattn/go-sqlite3"
    "github.com/google/uuid"
)

var db *sql.DB

func init() {
    var err error
    db, err = sql.Open("sqlite3", "db.sqlite3")
    if err != nil {
        log.Fatal(err)
    }

    // Create the clicks table if it doesn't exist
    createTableSQL := `CREATE TABLE IF NOT EXISTS clicks (
        id TEXT PRIMARY KEY,
        timestamp DATETIME
    );`
    if _, err := db.Exec(createTableSQL); err != nil {
        log.Fatal(err)
    }
}

func registerClick(c *fiber.Ctx) error {
    clickID := uuid.New().String()
    timestamp := time.Now()

    _, err := db.Exec("INSERT INTO clicks (id, timestamp) VALUES (?, ?)", clickID, timestamp)
    if err != nil {
        return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid request"})
    }

    return c.Status(http.StatusCreated).JSON(fiber.Map{"id": clickID, "timestamp": timestamp})
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

    var clicks []fiber.Map
    for rows.Next() {
        var id string
        var timestamp time.Time
        if err := rows.Scan(&id, &timestamp); err != nil {
            return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Internal server error"})
        }
        clicks = append(clicks, fiber.Map{"id": id, "timestamp": timestamp})
    }

    if len(clicks) == 0 {
        return c.Status(http.StatusNotFound).JSON(fiber.Map{"error": "No clicks found"})
    }

    return c.JSON(clicks)
}

func main() {
    app := fiber.New()

    app.Post("/click", registerClick)
    app.Get("/clicks", retrieveClicks)

    log.Fatal(app.Listen(":5000"))
}