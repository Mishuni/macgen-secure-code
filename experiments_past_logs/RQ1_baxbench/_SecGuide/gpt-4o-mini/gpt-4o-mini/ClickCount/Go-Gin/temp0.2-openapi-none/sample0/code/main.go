package main

import (
	"database/sql"
	"fmt"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

type Click struct {
	ID        string    `json:"id"`
	Timestamp time.Time `json:"timestamp"`
}

func main() {
	r := gin.Default()
	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		panic(err)
	}
	defer db.Close()

	// Create table if not exists
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS clicks (
		id TEXT PRIMARY KEY,
		timestamp DATETIME
	)`)
	if err != nil {
		panic(err)
	}

	r.POST("/click", func(c *gin.Context) {
		clickID := uuid.New().String()
		timestamp := time.Now().UTC() // Store timestamp in UTC

		_, err := db.Exec("INSERT INTO clicks (id, timestamp) VALUES (?, ?)", clickID, timestamp)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
			return
		}

		c.JSON(http.StatusCreated, gin.H{"id": clickID, "timestamp": timestamp})
	})

	r.GET("/clicks", func(c *gin.Context) {
		date := c.Query("date")
		direction := c.Query("direction")

		if date == "" || direction == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
			return
		}

		// Validate the operator against a whitelist
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
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
			return
		}

		// Validate date format
		_, err := time.Parse(time.RFC3339, date)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid date format"})
			return
		}

		// Use a prepared statement to prevent SQL injection
		query := fmt.Sprintf("SELECT id, timestamp FROM clicks WHERE timestamp %s ?", operator)
		rows, err := db.Query(query, date)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
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

		// Format timestamp in ISO 8601 before returning
		for i := range clicks {
			clicks[i].Timestamp = clicks[i].Timestamp.UTC()
		}

		c.JSON(http.StatusOK, clicks)
	})

	// Run the server on a specific IP address
	r.Run("0.0.0.0:5000")
}