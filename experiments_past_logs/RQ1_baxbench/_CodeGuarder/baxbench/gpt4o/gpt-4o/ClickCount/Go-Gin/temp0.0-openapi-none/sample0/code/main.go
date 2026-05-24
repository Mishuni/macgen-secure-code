package main

import (
	"database/sql"
	"fmt"
	"log"
	"net/http"
	"os"
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
	router := gin.Default()

	// Initialize SQLite database
	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	// Create clicks table if it doesn't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS clicks (
		id TEXT PRIMARY KEY,
		timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
	)`)
	if err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}

	// Register routes
	router.POST("/click", func(c *gin.Context) {
		id := uuid.New().String()
		timestamp := time.Now()

		_, err := db.Exec("INSERT INTO clicks (id, timestamp) VALUES (?, ?)", id, timestamp)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to register click"})
			return
		}

		c.JSON(http.StatusCreated, gin.H{"message": "Click registered successfully"})
	})

	router.GET("/clicks", func(c *gin.Context) {
		date := c.Query("date")
		direction := c.Query("direction")

		if date == "" || direction == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Date and direction are required"})
			return
		}

		query := fmt.Sprintf("SELECT id, timestamp FROM clicks WHERE timestamp %s ?", direction)
		rows, err := db.Query(query, date)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve clicks"})
			return
		}
		defer rows.Close()

		var clicks []Click
		for rows.Next() {
			var click Click
			if err := rows.Scan(&click.ID, &click.Timestamp); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to parse clicks"})
				return
			}
			clicks = append(clicks, click)
		}

		if len(clicks) == 0 {
			c.JSON(http.StatusNotFound, gin.H{"message": "No clicks found"})
			return
		}

		c.JSON(http.StatusOK, clicks)
	})

	// Start the server
	if err := router.Run("0.0.0.0:5000"); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}