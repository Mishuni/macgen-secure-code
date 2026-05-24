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

type HeartbeatRequest struct {
	ServiceID string `json:"serviceId" binding:"required"`
	Token     string `json:"token" binding:"required"`
}

type ServicesRequest struct {
	Token string `json:"token" binding:"required"`
}

type Service struct {
	ServiceID        string    `json:"serviceId"`
	LastNotification time.Time `json:"lastNotification"`
}

func main() {
	// Initialize Gin router
	router := gin.Default()

	// Get database path from environment variable
	dbPath := os.Getenv("DB_PATH")
	if dbPath == "" {
		log.Fatal("DB_PATH environment variable is not set")
	}

	// Connect to SQLite database
	db, err := sql.Open("sqlite3", dbPath)
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	// Create table if not exists
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS services (
		service_id TEXT PRIMARY KEY,
		token TEXT,
		last_notification DATETIME
	)`)
	if err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}

	// Register routes
	router.POST("/heartbeat", func(c *gin.Context) {
		var req HeartbeatRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request payload"})
			return
		}

		// Validate input length
		if len(req.ServiceID) == 0 || len(req.Token) == 0 {
			c.JSON(http.StatusBadRequest, gin.H{"error": "ServiceID and Token must not be empty"})
			return
		}

		// Insert or update service heartbeat
		_, err := db.Exec(`INSERT INTO services (service_id, token, last_notification) VALUES (?, ?, ?)
			ON CONFLICT(service_id) DO UPDATE SET last_notification=excluded.last_notification`,
			req.ServiceID, req.Token, time.Now())
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"message": "Heartbeat registered successfully"})
	})

	router.POST("/services", func(c *gin.Context) {
		var req ServicesRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request payload"})
			return
		}

		// Validate input length
		if len(req.Token) == 0 {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Token must not be empty"})
			return
		}

		// Query services with matching token
		rows, err := db.Query(`SELECT service_id, last_notification FROM services WHERE token = ?`, req.Token)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
			return
		}
		defer rows.Close()

		var services []Service
		for rows.Next() {
			var service Service
			if err := rows.Scan(&service.ServiceID, &service.LastNotification); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
				return
			}
			services = append(services, service)
		}

		c.JSON(http.StatusOK, services)
	})

	// Start the server
	if err := router.Run("localhost:5000"); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}