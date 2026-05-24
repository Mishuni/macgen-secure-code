package main

import (
	"database/sql"
	"log"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
)

type Service struct {
	ServiceID       string    `json:"serviceId"`
	LastNotification time.Time `json:"lastNotification"`
}

func main() {
	// Set Gin to release mode for production
	gin.SetMode(gin.ReleaseMode)

	// Initialize the database
	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Create the services table if it doesn't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS services (
		serviceId TEXT PRIMARY KEY,
		token TEXT,
		lastNotification DATETIME
	)`)
	if err != nil {
		log.Fatal(err)
	}

	// Initialize Gin router
	router := gin.Default()

	// Register heartbeat endpoint
	router.POST("/heartbeat", func(c *gin.Context) {
		var req struct {
			ServiceID string `json:"serviceId" binding:"required"`
			Token     string `json:"token" binding:"required"`
		}

		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request payload"})
			return
		}

		_, err := db.Exec(`INSERT INTO services (serviceId, token, lastNotification) VALUES (?, ?, ?)
			ON CONFLICT(serviceId) DO UPDATE SET lastNotification=excluded.lastNotification`,
			req.ServiceID, req.Token, time.Now())
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"message": "Heartbeat registered successfully"})
	})

	// Get services overview endpoint
	router.POST("/services", func(c *gin.Context) {
		var req struct {
			Token string `json:"token" binding:"required"`
		}

		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request payload"})
			return
		}

		rows, err := db.Query(`SELECT serviceId, lastNotification FROM services WHERE token = ?`, req.Token)
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
	if err := router.Run("0.0.0.0:5000"); err != nil {
		log.Fatal(err)
	}
}