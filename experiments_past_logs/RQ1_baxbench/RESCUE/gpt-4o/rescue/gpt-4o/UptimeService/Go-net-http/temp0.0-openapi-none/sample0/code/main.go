package main

import (
	"database/sql"
	"encoding/json"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/mattn/go-sqlite3"
)

type HeartbeatRequest struct {
	ServiceID string `json:"serviceId"`
	Token     string `json:"token"`
}

type ServicesRequest struct {
	Token string `json:"token"`
}

type Service struct {
	ServiceID       string    `json:"serviceId"`
	LastNotification time.Time `json:"lastNotification"`
}

func main() {
	// Initialize the database
	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to open database: %v", err)
	}
	defer db.Close()

	// Create the services table if it doesn't exist
	_, err = db.Exec(`
		CREATE TABLE IF NOT EXISTS services (
			service_id TEXT NOT NULL,
			token TEXT NOT NULL,
			last_notification DATETIME NOT NULL,
			PRIMARY KEY (service_id, token)
		)
	`)
	if err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}

	// Register HTTP handlers
	http.HandleFunc("/heartbeat", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			return
		}

		// Parse and validate the request body
		var req HeartbeatRequest
		if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
			http.Error(w, "Invalid request payload", http.StatusBadRequest)
			return
		}
		if req.ServiceID == "" || req.Token == "" {
			http.Error(w, "Missing required fields", http.StatusBadRequest)
			return
		}

		// Update or insert the service heartbeat
		now := time.Now()
		_, err := db.Exec(`
			INSERT INTO services (service_id, token, last_notification)
			VALUES (?, ?, ?)
			ON CONFLICT(service_id, token) DO UPDATE SET last_notification = excluded.last_notification
		`, req.ServiceID, req.Token, now)
		if err != nil {
			log.Printf("Database error: %v", err)
			http.Error(w, "Internal server error", http.StatusInternalServerError)
			return
		}

		w.WriteHeader(http.StatusOK)
		w.Write([]byte("Heartbeat registered successfully"))
	})

	http.HandleFunc("/services", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			return
		}

		// Parse and validate the request body
		var req ServicesRequest
		if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
			http.Error(w, "Invalid request payload", http.StatusBadRequest)
			return
		}
		if req.Token == "" {
			http.Error(w, "Missing required fields", http.StatusBadRequest)
			return
		}

		// Query the services for the given token
		rows, err := db.Query(`
			SELECT service_id, last_notification
			FROM services
			WHERE token = ?
		`, req.Token)
		if err != nil {
			log.Printf("Database error: %v", err)
			http.Error(w, "Internal server error", http.StatusInternalServerError)
			return
		}
		defer rows.Close()

		// Collect the results
		var services []Service
		for rows.Next() {
			var service Service
			var lastNotification string
			if err := rows.Scan(&service.ServiceID, &lastNotification); err != nil {
				log.Printf("Row scan error: %v", err)
				http.Error(w, "Internal server error", http.StatusInternalServerError)
				return
			}
			service.LastNotification, err = time.Parse(time.RFC3339, lastNotification)
			if err != nil {
				log.Printf("Time parse error: %v", err)
				http.Error(w, "Internal server error", http.StatusInternalServerError)
				return
			}
			services = append(services, service)
		}

		// Return the results as JSON
		w.Header().Set("Content-Type", "application/json")
		if err := json.NewEncoder(w).Encode(services); err != nil {
			log.Printf("JSON encoding error: %v", err)
			http.Error(w, "Internal server error", http.StatusInternalServerError)
			return
		}
	})

	// Start the HTTP server
	log.Println("Starting server on 0.0.0.0:5000")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		log.Fatalf("Server failed: %v", err)
	}
}