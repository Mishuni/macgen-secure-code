package main

import (
	"database/sql"
	"encoding/json"
	"net/http"
	"os"
	"time"

	"github.com/mattn/go-sqlite3"
	"regexp"
	"log"
)

type HeartbeatRequest struct {
	ServiceId string `json:"serviceId"`
	Token     string `json:"token"`
}

type ServicesRequest struct {
	Token string `json:"token"`
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
		log.Fatalf("Failed to open database: %v", err)
	}

	// Create table if not exists
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS services (
		id TEXT PRIMARY KEY,
		token TEXT NOT NULL,
		last_notification DATETIME
	)`)
	if err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}
}

func validateServiceId(serviceId string) bool {
	// Example validation: check if the serviceId is a valid UUID
	re := regexp.MustCompile(`^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$`)
	return re.MatchString(serviceId)
}

func validateToken(token string) bool {
	// Example validation: check if the token is not empty
	return len(token) > 0
}

func registerHeartbeat(w http.ResponseWriter, r *http.Request) {
	var req HeartbeatRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request payload", http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	if !validateServiceId(req.ServiceId) || !validateToken(req.Token) {
		http.Error(w, "Invalid ServiceId or Token", http.StatusBadRequest)
		return
	}

	_, err := db.Exec(`INSERT OR REPLACE INTO services (id, token, last_notification) VALUES (?, ?, ?)`,
		req.ServiceId, req.Token, time.Now())
	if err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
}

func getServices(w http.ResponseWriter, r *http.Request) {
	var req ServicesRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request payload", http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	if !validateToken(req.Token) {
		http.Error(w, "Invalid Token", http.StatusBadRequest)
		return
	}

	rows, err := db.Query(`SELECT id, last_notification FROM services WHERE token = ?`, req.Token)
	if err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var services []ServiceStatus
	for rows.Next() {
		var service ServiceStatus
		if err := rows.Scan(&service.ServiceId, &service.LastNotification); err != nil {
			http.Error(w, "Internal server error", http.StatusInternalServerError)
			return
		}
		services = append(services, service)
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(services)
}

func main() {
	http.HandleFunc("/heartbeat", registerHeartbeat)
	http.HandleFunc("/services", getServices)

	// Use HTTPS in production, for now, we will use HTTP for simplicity
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}