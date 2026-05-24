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
	ServiceId string `json:"serviceId" binding:"required"`
	Token     string `json:"token" binding:"required"`
}

type ServicesRequest struct {
	Token string `json:"token" binding:"required"`
}

type ServiceStatus struct {
	ServiceId        string    `json:"serviceId"`
	LastNotification time.Time `json:"lastNotification"`
}

var db *sql.DB

func init() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		panic(err)
	}

	createTableSQL := `CREATE TABLE IF NOT EXISTS heartbeats (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		serviceId TEXT NOT NULL,
		token TEXT NOT NULL,
		lastNotification DATETIME DEFAULT CURRENT_TIMESTAMP
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		panic(err)
	}
}

func registerHeartbeat(c *gin.Context) {
	var req HeartbeatRequest
	if err := c.ShouldBindJSON(&req); err != nil || req.ServiceId == "" || len(req.Token) < 1 || len(req.ServiceId) < 1 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request payload."})
		return
	}

	_, err := db.Exec("INSERT INTO heartbeats (serviceId, token, lastNotification) VALUES (?, ?, ?)",
		req.ServiceId, req.Token, time.Now())
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error."})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Heartbeat registered successfully."})
}

func getServices(c *gin.Context) {
	var req ServicesRequest
	if err := c.ShouldBindJSON(&req); err != nil || req.Token == "" || len(req.Token) < 1 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request payload."})
		return
	}

	rows, err := db.Query("SELECT serviceId, lastNotification FROM heartbeats WHERE token = ?", req.Token)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error."})
		return
	}
	defer rows.Close()

	var services []ServiceStatus
	for rows.Next() {
		var service ServiceStatus
		if err := rows.Scan(&service.ServiceId, &service.LastNotification); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error."})
			return
		}
		services = append(services, service)
	}

	c.JSON(http.StatusOK, services)
}

func main() {
	r := gin.Default()
	r.POST("/heartbeat", registerHeartbeat)
	r.POST("/services", getServices)
	r.Run("0.0.0.0:5000")
}