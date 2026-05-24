package main

import (
	"database/sql"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
	"github.com/google/uuid"
)

func main() {
	// Initialize Gin router
	router := gin.Default()

	// Initialize SQLite database
	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	// Create the clicks table if it doesn't exist
	_, err = db.Exec(`
		CREATE TABLE IF NOT EXISTS clicks (
			id TEXT PRIMARY KEY,
			timestamp TEXT NOT NULL
		)
	`)
	if err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}

	// POST /click - Register a click
	router.POST("/click", func(c *gin.Context) {
		// Generate a unique ID for the click
		id := uuid.New().String()
		timestamp := time.Now().UTC().Format(time.RFC3339)

		// Insert the click into the database
		_, err := db.Exec("INSERT INTO clicks (id, timestamp) VALUES (?, ?)", id, timestamp)
		if err != nil {
			log.Printf("Failed to insert click: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to register click"})
			return
		}

		c.JSON(http.StatusCreated, gin.H{"message": "Click registered successfully"})
	})

	// GET /clicks - Retrieve clicks
	router.GET("/clicks", func(c *gin.Context) {
		// Get query parameters
		date := c.Query("date")
		direction := c.Query("direction")

		// Validate query parameters
		if date == "" || direction == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Both 'date' and 'direction' query parameters are required"})
			return
		}

		if direction != "<" && direction != ">" && direction != "<=" && direction != ">=" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid 'direction' value"})
			return
		}

		// Query the database for clicks
		query := "SELECT id, timestamp FROM clicks WHERE timestamp " + direction + " ?"
		rows, err := db.Query(query, date)
		if err != nil {
			log.Printf("Failed to query clicks: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve clicks"})
			return
		}
		defer rows.Close()

		// Parse the results
		var clicks []map[string]string
		for rows.Next() {
			var id, timestamp string
			if err := rows.Scan(&id, &timestamp); err != nil {
				log.Printf("Failed to scan row: %v", err)
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve clicks"})
				return
			}
			clicks = append(clicks, map[string]string{"id": id, "timestamp": timestamp})
		}

		// Check if no clicks were found
		if len(clicks) == 0 {
			c.JSON(http.StatusNotFound, gin.H{"error": "No clicks found"})
			return
		}

		c.JSON(http.StatusOK, clicks)
	})

	// Start the server
	port := "5000"
	if os.Getenv("PORT") != "" {
		port = os.Getenv("PORT")
	}
	router.Run("0.0.0.0:" + port)
}