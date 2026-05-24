package main

import (
	"database/sql"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
)

const (
	dbFileName = "db.sqlite3"
)

func main() {
	// Initialize Gin router
	router := gin.Default()

	// Initialize the database
	db, err := initDB()
	if err != nil {
		log.Fatalf("Failed to initialize database: %v", err)
	}
	defer db.Close()

	// Define routes
	router.POST("/heartbeat", func(c *gin.Context) {
		var req struct {
			ServiceID string `json:"serviceId" binding:"required"`
			Token     string `json:"token" binding:"required"`
		}

		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request payload"})
			return
		}

		// Register heartbeat
		if err := registerHeartbeat(db, req.ServiceID, req.Token); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"message": "Heartbeat registered successfully"})
	})

	router.POST("/services", func(c *gin.Context) {
		var req struct {
			Token string `json:"token" binding:"required"`
		}

		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request payload"})
			return
		}

		// Get services overview
		services, err := getServicesOverview(db, req.Token)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
			return
		}

		c.JSON(http.StatusOK, services)
	})

	// Start the server
	if err := router.Run("0.0.0.0:5000"); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}

func initDB() (*sql.DB, error) {
	db, err := sql.Open("sqlite3", dbFileName)
	if err != nil {
		return nil, err
	}

	createTableQuery := `
	CREATE TABLE IF NOT EXISTS services (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		service_id TEXT NOT NULL,
		token TEXT NOT NULL,
		last_notification DATETIME NOT NULL
	);
	`
	if _, err := db.Exec(createTableQuery); err != nil {
		return nil, err
	}

	return db, nil
}

func registerHeartbeat(db *sql.DB, serviceID, token string) error {
	now := time.Now().UTC()
	query := `
	INSERT INTO services (service_id, token, last_notification)
	VALUES (?, ?, ?)
	ON CONFLICT(service_id) DO UPDATE SET last_notification=excluded.last_notification;
	`
	_, err := db.Exec(query, serviceID, token, now)
	return err
}

func getServicesOverview(db *sql.DB, token string) ([]map[string]interface{}, error) {
	query := `
	SELECT service_id, last_notification FROM services WHERE token = ?;
	`
	rows, err := db.Query(query, token)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var services []map[string]interface{}
	for rows.Next() {
		var serviceID string
		var lastNotification time.Time
		if err := rows.Scan(&serviceID, &lastNotification); err != nil {
			return nil, err
		}
		service := map[string]interface{}{
			"serviceId":       serviceID,
			"lastNotification": lastNotification.Format(time.RFC3339),
		}
		services = append(services, service)
	}

	return services, nil
}