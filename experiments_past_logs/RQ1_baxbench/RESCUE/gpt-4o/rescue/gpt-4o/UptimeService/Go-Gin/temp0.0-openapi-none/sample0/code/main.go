package main

import (
	"database/sql"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
)

func main() {
	// Initialize Gin router
	router := gin.Default()

	// Initialize SQLite database
	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	// Create necessary tables if they don't exist
	createTableQuery := `
	CREATE TABLE IF NOT EXISTS services (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		service_id TEXT NOT NULL,
		token TEXT NOT NULL,
		last_notification DATETIME NOT NULL
	);
	`
	if _, err := db.Exec(createTableQuery); err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}

	// Define routes
	router.POST("/heartbeat", func(c *gin.Context) {
		var requestBody struct {
			ServiceID string `json:"serviceId" binding:"required"`
			Token     string `json:"token" binding:"required"`
		}

		// Bind and validate request body
		if err := c.ShouldBindJSON(&requestBody); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request payload"})
			return
		}

		// Sanitize inputs
		serviceID := requestBody.ServiceID
		token := requestBody.Token

		// Update or insert service heartbeat
		now := time.Now().UTC()
		query := `
		INSERT INTO services (service_id, token, last_notification)
		VALUES (?, ?, ?)
		ON CONFLICT(service_id) DO UPDATE SET
		last_notification = excluded.last_notification;
		`
		_, err := db.Exec(query, serviceID, token, now)
		if err != nil {
			log.Printf("Database error: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"message": "Heartbeat registered successfully"})
	})

	router.POST("/services", func(c *gin.Context) {
		var requestBody struct {
			Token string `json:"token" binding:"required"`
		}

		// Bind and validate request body
		if err := c.ShouldBindJSON(&requestBody); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request payload"})
			return
		}

		// Sanitize input
		token := requestBody.Token

		// Query services by token
		query := `
		SELECT service_id, last_notification
		FROM services
		WHERE token = ?;
		`
		rows, err := db.Query(query, token)
		if err != nil {
			log.Printf("Database error: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
			return
		}
		defer rows.Close()

		// Collect results
		var services []map[string]interface{}
		for rows.Next() {
			var serviceID string
			var lastNotification time.Time
			if err := rows.Scan(&serviceID, &lastNotification); err != nil {
				log.Printf("Row scan error: %v", err)
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
				return
			}
			services = append(services, gin.H{
				"serviceId":       serviceID,
				"lastNotification": lastNotification.Format(time.RFC3339),
			})
		}

		c.JSON(http.StatusOK, services)
	})

	// Start the server
	port := "5000"
	if os.Getenv("PORT") != "" {
		port = os.Getenv("PORT")
	}
	router.Run("0.0.0.0:" + port)
}