package main

import (
	"database/sql"
	"log"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
)

func main() {
	// Initialize Gin router
	r := gin.Default()

	// Initialize SQLite database
	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Create table if not exists
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS services (
		serviceId TEXT PRIMARY KEY,
		token TEXT,
		lastNotification DATETIME
	)`)
	if err != nil {
		log.Fatal(err)
	}

	// Register routes
	r.POST("/heartbeat", func(c *gin.Context) {
		var req struct {
			ServiceId string `json:"serviceId" binding:"required"`
			Token     string `json:"token" binding:"required"`
		}

		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request payload"})
			return
		}

		_, err := db.Exec(`INSERT INTO services (serviceId, token, lastNotification) VALUES (?, ?, ?)
			ON CONFLICT(serviceId) DO UPDATE SET lastNotification=excluded.lastNotification`,
			req.ServiceId, req.Token, time.Now())
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"message": "Heartbeat registered successfully"})
	})

	r.POST("/services", func(c *gin.Context) {
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

		var services []gin.H
		for rows.Next() {
			var serviceId string
			var lastNotification time.Time
			if err := rows.Scan(&serviceId, &lastNotification); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
				return
			}
			services = append(services, gin.H{
				"serviceId":       serviceId,
				"lastNotification": lastNotification,
			})
		}

		c.JSON(http.StatusOK, services)
	})

	// Start the server
	if err := r.Run("0.0.0.0:5000"); err != nil {
		log.Fatal(err)
	}
}