package main

import (
	"database/sql"
	"encoding/json"
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

func initDB() {
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

func isValidDate(date string) bool {
	_, err := time.Parse("2006-01-02", date)
	return err == nil
}

func isValidDirection(direction string) bool {
	validDirections := map[string]bool{
		"<":  true,
		"<=": true,
		">":  true,
		">=": true,
	}
	return validDirections[direction]
}

func registerClick(c *gin.Context) {
	var click Click
	if err := c.ShouldBindJSON(&click); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
		return
	}

	click.ID = uuid.NewString()
	click.Timestamp = time.Now()

	_, err := db.Exec("INSERT INTO clicks (id, timestamp) VALUES (?, ?)", click.ID, click.Timestamp)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Failed to register click"})
		return
	}

	c.JSON(http.StatusCreated, click)
}

func retrieveClicks(c *gin.Context) {
	date := c.Query("date")
	direction := c.Query("direction")

	if !isValidDate(date) || !isValidDirection(direction) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	operator := direction
	rows, err := db.Query("SELECT id, timestamp FROM clicks WHERE timestamp "+operator+" ?", date)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Failed to retrieve clicks"})
		return
	}
	defer rows.Close()

	var clicks []Click
	for rows.Next() {
		var click Click
		if err := rows.Scan(&click.ID, &click.Timestamp); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Failed to scan click"})
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
	initDB()
	defer db.Close()

	r := gin.Default()
	r.POST("/click", registerClick)
	r.GET("/clicks", retrieveClicks)

	if err := r.Run("0.0.0.0:5000"); err != nil {
		panic(err)
	}
}