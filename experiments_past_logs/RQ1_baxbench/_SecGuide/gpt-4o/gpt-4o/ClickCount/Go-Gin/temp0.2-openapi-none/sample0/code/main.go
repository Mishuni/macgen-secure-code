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
	router := gin.Default()

	// Initialize SQLite database with a connection pool
	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to open database: %v", err)
	}
	defer db.Close()

	// Set database connection pool settings
	db.SetMaxOpenConns(10)
	db.SetMaxIdleConns(5)
	db.SetConnMaxLifetime(time.Hour)

	// Create clicks table if it doesn't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS clicks (
		id TEXT PRIMARY KEY,
		timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
	)`)
	if err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}

	// Register a click
	router.POST("/click", func(c *gin.Context) {
		id := uuid.New().String()
		_, err := db.Exec("INSERT INTO clicks (id) VALUES (?)", id)
		if err != nil {
			log.Printf("Error registering click: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to register click"})
			return
		}
		c.JSON(http.StatusCreated, gin.H{"message": "Click registered successfully"})
	})

	// Retrieve clicks
	router.GET("/clicks", func(c *gin.Context) {
		date := c.Query("date")
		direction := c.Query("direction")

		// Validate input
		if date == "" || direction == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Date and direction are required"})
			return
		}

		// Validate direction against a whitelist
		validDirections := map[string]string{"<": "<", "<=": "<=", ">": ">", ">=": ">="}
		validDirection, ok := validDirections[direction]
		if !ok {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid direction"})
			return
		}

		// Validate date format
		parsedDate, err := time.Parse("2006-01-02", date)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid date format"})
			return
		}

		// Validate date is not in the future
		if parsedDate.After(time.Now()) {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Date cannot be in the future"})
			return
		}

		// Use parameterized query to prevent SQL injection
		query := "SELECT id, timestamp FROM clicks WHERE timestamp " + validDirection + " ?"
		rows, err := db.Query(query, date)
		if err != nil {
			log.Printf("Error retrieving clicks: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve clicks"})
			return
		}
		defer rows.Close()

		var clicks []map[string]interface{}
		for rows.Next() {
			var id string
			var timestamp time.Time
			if err := rows.Scan(&id, &timestamp); err != nil {
				log.Printf("Error scanning row: %v", err)
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve clicks"})
				return
			}
			clicks = append(clicks, gin.H{"id": id, "timestamp": timestamp})
		}

		if len(clicks) == 0 {
			c.JSON(http.StatusNotFound, gin.H{"error": "No clicks found"})
			return
		}

		c.JSON(http.StatusOK, clicks)
	})

	// Start the server
	if err := router.Run("0.0.0.0:5000"); err != nil {
		log.Fatalf("Failed to run server: %v", err)
	}
}