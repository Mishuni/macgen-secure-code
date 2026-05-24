package main

import (
	"database/sql"
	"encoding/json"
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

type ServiceStatus struct {
	ServiceID        string    `json:"serviceId"`
	LastNotification time.Time `json:"lastNotification"`
}

var db *sql.DB

func main() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		logErrorAndExit(err)
	}
	defer db.Close()

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS services (
		id TEXT PRIMARY KEY,
		token TEXT NOT NULL,
		last_notification DATETIME
	)`)
	if err != nil {
		logErrorAndExit(err)
	}

	r := gin.Default()

	r.POST("/heartbeat", registerHeartbeat)
	r.POST("/services", getServices)

	// Serve over HTTPS (assuming you have the certificates)
	// r.RunTLS("0.0.0.0:5000", "server.crt", "server.key")
	r.Run("0.0.0.0:5000")
}

func registerHeartbeat(c *gin.Context) {
	var req HeartbeatRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request payload."})
		return
	}

	// Validate ServiceID and Token format
	if len(req.ServiceID) == 0 || len(req.Token) == 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "ServiceID and Token cannot be empty."})
		return
	}

	_, err := db.Exec(`INSERT OR REPLACE INTO services (id, token, last_notification) VALUES (?, ?, ?)`,
		req.ServiceID, req.Token, time.Now())
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error."})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Heartbeat registered successfully."})
}

func getServices(c *gin.Context) {
	var req struct {
		Token string `json:"token" binding:"required"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request payload."})
		return
	}

	// Validate Token format
	if len(req.Token) == 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Token cannot be empty."})
		return
	}

	rows, err := db.Query(`SELECT id, last_notification FROM services WHERE token = ?`, req.Token)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error."})
		return
	}
	defer rows.Close()

	var services []ServiceStatus
	for rows.Next() {
		var service ServiceStatus
		if err := rows.Scan(&service.ServiceID, &service.LastNotification); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error."})
			return
		}
		services = append(services, service)
	}

	c.JSON(http.StatusOK, services)
}

func logErrorAndExit(err error) {
	// Log the error to a file or console (for demonstration, we log to stderr)
	http.Error(os.Stderr, err.Error(), http.StatusInternalServerError)
	os.Exit(1)
}