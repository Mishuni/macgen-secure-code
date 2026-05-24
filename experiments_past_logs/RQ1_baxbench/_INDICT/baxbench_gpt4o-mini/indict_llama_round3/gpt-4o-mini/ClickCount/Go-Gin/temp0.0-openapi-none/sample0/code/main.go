package main

import (
	"database/sql"
	"net/http"
	"os"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

type Click struct {
	ID        string    `json:"id"`
	Timestamp time.Time `json:"timestamp"`
}

var db *sql.DB

func init() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		panic(err)
	}

	createTableSQL := `CREATE TABLE IF NOT EXISTS clicks (
		id TEXT PRIMARY KEY,
		timestamp DATETIME
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		panic(err)
	}
}

func registerClick(c *gin.Context) {
	click := Click{
		ID:        uuid.NewString(),
		Timestamp: time.Now(),
	}

	_, err := db.Exec("INSERT INTO clicks (id, timestamp) VALUES (?, ?)", click.ID, click.Timestamp)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
		return
	}

	c.JSON(http.StatusCreated, click)
}

func retrieveClicks(c *gin.Context) {
	date := c.Query("date")
	direction := c.Query("direction")

	if date == "" || direction == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
		return
	}

	var operator string
	switch direction {
	case "<", "<=", ">", ">=":
		operator = direction
	default:
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid direction"})
		return
	}

	query := "SELECT id, timestamp FROM clicks WHERE timestamp " + operator + " ?"
	rows, err := db.Query(query, date)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
		return
	}
	defer rows.Close()

	var clicks []Click
	for rows.Next() {
		var click Click
		if err := rows.Scan(&click.ID, &click.Timestamp); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
			return
		}
		clicks = append(clicks, click)
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

	if err := r.Run("0.0.0.0:5000"); err != nil {
		panic(err)
	}
}