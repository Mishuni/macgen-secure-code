package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
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

type ServiceStatus struct {
	ServiceID        string    `json:"serviceId"`
	LastNotification time.Time `json:"lastNotification"`
}

var db *sql.DB

func init() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to open database: %v", err)
	}

	createTableSQL := `CREATE TABLE IF NOT EXISTS heartbeats (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		service_id TEXT NOT NULL,
		last_notification TIMESTAMP NOT NULL,
		token TEXT NOT NULL
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}
}

func main() {
	router := gin.Default()

	router.POST("/heartbeat", registerHeartbeat)
	router.POST("/services", getServices)

	if err := router.Run("0.0.0.0:5000"); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}

func registerHeartbeat(c *gin.Context) {
	var req HeartbeatRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request payload."})
		return
	}

	_, err := db.Exec("INSERT INTO heartbeats (service_id, last_notification, token) VALUES (?, ?, ?)",
		req.ServiceID, time.Now(), req.Token)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error."})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Heartbeat registered successfully."})
}

func getServices(c *gin.Context) {
	var req ServicesRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request payload."})
		return
	}

	rows, err := db.Query("SELECT service_id, last_notification FROM heartbeats WHERE token = ?", req.Token)
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