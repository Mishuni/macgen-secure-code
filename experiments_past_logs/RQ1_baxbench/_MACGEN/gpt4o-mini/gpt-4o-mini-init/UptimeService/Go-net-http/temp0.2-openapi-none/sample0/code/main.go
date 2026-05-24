package main

import (
	"encoding/json"
	"net/http"
	"os"
	"time"

	"database/sql"
	"github.com/mattn/go-sqlite3"
)

var db *sql.DB

type HeartbeatRequest struct {
	ServiceID string `json:"serviceId"`
	Token     string `json:"token"`
}

type Service struct {
	ID               string    `json:"serviceId"`
	LastNotification time.Time `json:"lastNotification"`
}

func init() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		panic(err)
	}
	// Create table if not exists
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS services (
		id TEXT PRIMARY KEY,
		token TEXT,
		last_notification DATETIME
	)`)
	if err != nil {
		panic(err)
	}
}

func registerHeartbeat(w http.ResponseWriter, r *http.Request) {
	var req HeartbeatRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil || req.ServiceID == "" || req.Token == "" {
		http.Error(w, "Invalid request payload", http.StatusBadRequest)
		return
	}
	now := time.Now()
	_, err := db.Exec("INSERT OR REPLACE INTO services (id, token, last_notification) VALUES (?, ?, ?)", req.ServiceID, req.Token, now)
	if err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}
	w.WriteHeader(http.StatusOK)
}

func getServices(w http.ResponseWriter, r *http.Request) {
	var req struct {
		Token string `json:"token"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil || req.Token == "" {
		http.Error(w, "Invalid request payload", http.StatusBadRequest)
		return
	}
	rows, err := db.Query("SELECT id, last_notification FROM services WHERE token = ?", req.Token)
	if err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}
	defer rows.Close()
	var services []Service
	for rows.Next() {
		var service Service
		if err := rows.Scan(&service.ID, &service.LastNotification); err != nil {
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
	http.ListenAndServe("0.0.0.0:5000", nil)
}