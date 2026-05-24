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

	// Set up SQLite database
	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Create clicks table if it doesn't exist
	createTableSQL := `CREATE TABLE IF NOT EXISTS clicks (
		id TEXT PRIMARY KEY,
		timestamp DATETIME
	);`
	if _, err := db.Exec(createTableSQL); err != nil {
		log.Fatal(err)
	}

	// Register click endpoint
	router.POST("/click", func(c *gin.Context) {
		var click Click
		click.ID = uuid.NewString()
		click.Timestamp = time.Now()

		// Insert click into database
		_, err := db.Exec("INSERT INTO clicks (id, timestamp) VALUES (?, ?)", click.ID, click.Timestamp)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
			return
		}

		c.JSON(http.StatusCreated, click)
	})

	// Retrieve clicks endpoint
	router.GET("/clicks", func(c *gin.Context) {
		date := c.Query("date")
		direction := c.Query("direction")

		if date == "" || direction == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
			return
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
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid direction"})
			return
		}

		query := fmt.Sprintf("SELECT id, timestamp FROM clicks WHERE timestamp %s ?", operator)
		rows, err := db.Query(query, date)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Database query error"})
			return
		}
		defer rows.Close()

		var clicks []Click
		for rows.Next() {
			var click Click
			if err := rows.Scan(&click.ID, &click.Timestamp); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Error scanning results"})
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

	// Start server
	if err := router.Run("0.0.0.0:5000"); err != nil {
		log.Fatal(err)
	}
}