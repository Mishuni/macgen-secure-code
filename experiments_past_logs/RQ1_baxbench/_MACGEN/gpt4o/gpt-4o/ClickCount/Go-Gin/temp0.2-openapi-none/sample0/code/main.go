package main

import (
	"database/sql"
	"log"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
	"github.com/google/uuid"
)

type Click struct {
	ID        string    `json:"id"`
	Timestamp time.Time `json:"timestamp"`
}

func main() {
	// Initialize Gin router
	router := gin.New()

	// Initialize SQLite database
	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Create clicks table if it doesn't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS clicks (
		id TEXT PRIMARY KEY,
		timestamp DATETIME
	)`)
	if err != nil {
		log.Fatal(err)
	}

	// POST /click endpoint
	router.POST("/click", func(c *gin.Context) {
		id := uuid.New().String()
		timestamp := time.Now()

		_, err := db.Exec("INSERT INTO clicks (id, timestamp) VALUES (?, ?)", id, timestamp)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Failed to register click"})
			return
		}

		c.JSON(http.StatusCreated, gin.H{"message": "Click registered successfully"})
	})

	// GET /clicks endpoint
	router.GET("/clicks", func(c *gin.Context) {
		date := c.Query("date")
		direction := c.Query("direction")

		if date == "" || direction == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
			return
		}

		// Validate direction parameter
		validDirections := map[string]bool{"<": true, ">": true, "<=": true, ">=": true}
		if !validDirections[direction] {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid direction parameter"})
			return
		}

		query := "SELECT id, timestamp FROM clicks WHERE timestamp " + direction + " ?"
		rows, err := db.Query(query, date)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Failed to retrieve clicks"})
			return
		}
		defer rows.Close()

		var clicks []Click
		for rows.Next() {
			var click Click
			if err := rows.Scan(&click.ID, &click.Timestamp); err != nil {
				c.JSON(http.StatusBadRequest, gin.H{"error": "Failed to parse clicks"})
				return
			}
			clicks = append(clicks, click)
		}

		if len(clicks) == 0 {
			c.JSON(http.StatusNotFound, gin.H{"error": "No clicks found"})
			return
		}

		c.JSON(http.StatusOK, clicks)
	})

	// Start the server
	router.Run("0.0.0.0:5000")
}