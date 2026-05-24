package main

import (
	"database/sql"
	"log"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

func main() {
	// Initialize Gin router
	r := gin.Default()

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

	// Register a click
	r.POST("/click", func(c *gin.Context) {
		id := uuid.New().String()
		timestamp := time.Now().UTC()

		_, err := db.Exec("INSERT INTO clicks (id, timestamp) VALUES (?, ?)", id, timestamp)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Failed to register click"})
			return
		}

		c.JSON(http.StatusCreated, gin.H{"message": "Click registered successfully"})
	})

	// Retrieve clicks
	r.GET("/clicks", func(c *gin.Context) {
		dateStr := c.Query("date")
		direction := c.Query("direction")

		if dateStr == "" || direction == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Date and direction are required"})
			return
		}

		date, err := time.Parse("2006-01-02", dateStr)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid date format"})
			return
		}

		var operator string
		switch direction {
		case "<":
			operator = "<"
		case ">":
			operator = ">"
		case "<=":
			operator = "<="
		case ">=":
			operator = ">="
		default:
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid direction"})
			return
		}

		query := "SELECT id, timestamp FROM clicks WHERE timestamp " + operator + " ?"
		rows, err := db.Query(query, date)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve clicks"})
			return
		}
		defer rows.Close()

		var clicks []map[string]interface{}
		for rows.Next() {
			var id string
			var timestamp time.Time
			if err := rows.Scan(&id, &timestamp); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to parse clicks"})
				return
			}
			clicks = append(clicks, gin.H{"id": id, "timestamp": timestamp})
		}

		if len(clicks) == 0 {
			c.JSON(http.StatusNotFound, gin.H{"message": "No clicks found"})
			return
		}

		c.JSON(http.StatusOK, clicks)
	})

	// Start the server
	if err := r.Run("0.0.0.0:5000"); err != nil {
		log.Fatal(err)
	}
}