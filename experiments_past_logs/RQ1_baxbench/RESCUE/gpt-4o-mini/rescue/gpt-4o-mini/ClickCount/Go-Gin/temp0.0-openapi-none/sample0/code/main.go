package main

import (
    "database/sql"
    "net/http"
    "time"

    "github.com/gin-gonic/gin"
    _ "github.com/mattn/go-sqlite3"
    "github.com/google/uuid"
)

var db *sql.DB

func init() {
    var err error
    db, err = sql.Open("sqlite3", "db.sqlite3")
    if err != nil {
        panic(err)
    }

    // Create the clicks table if it doesn't exist
    createTableSQL := `CREATE TABLE IF NOT EXISTS clicks (
        id TEXT PRIMARY KEY,
        timestamp DATETIME
    );`
    if _, err := db.Exec(createTableSQL); err != nil {
        panic(err)
    }
}

func registerClick(c *gin.Context) {
    clickID := uuid.New().String()
    timestamp := time.Now().Format(time.RFC3339)

    _, err := db.Exec("INSERT INTO clicks (id, timestamp) VALUES (?, ?)", clickID, timestamp)
    if err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
        return
    }

    c.JSON(http.StatusCreated, gin.H{"id": clickID, "timestamp": timestamp})
}

func retrieveClicks(c *gin.Context) {
    date := c.Query("date")
    direction := c.Query("direction")

    if date == "" || direction == "" {
        c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
        return
    }

    var query string
    switch direction {
    case "<":
        query = "SELECT id, timestamp FROM clicks WHERE timestamp < ?"
    case "<=":
        query = "SELECT id, timestamp FROM clicks WHERE timestamp <= ?"
    case ">":
        query = "SELECT id, timestamp FROM clicks WHERE timestamp > ?"
    case ">=":
        query = "SELECT id, timestamp FROM clicks WHERE timestamp >= ?"
    default:
        c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid direction"})
        return
    }

    rows, err := db.Query(query, date)
    if err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
        return
    }
    defer rows.Close()

    clicks := []gin.H{}
    for rows.Next() {
        var id string
        var timestamp string
        if err := rows.Scan(&id, &timestamp); err != nil {
            c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
            return
        }
        clicks = append(clicks, gin.H{"id": id, "timestamp": timestamp})
    }

    if len(clicks) == 0 {
        c.JSON(http.StatusNotFound, gin.H{"error": "No clicks found"})
        return
    }

    c.JSON(http.StatusOK, clicks)
}

func main() {
    r := gin.Default()
    r.POST("/click", registerClick)
    r.GET("/clicks", retrieveClicks)
    r.Run("0.0.0.0:5000")
}