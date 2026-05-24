package main

import (
	"encoding/json"
	"net/http"
	"os"
	"time"

	"database/sql"
	"github.com/mattn/go-sqlite3"
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
		panic(err)
	}

	// Create table if it doesn't exist
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
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil || req.ServiceId == "" || req.Token == "" {
		http.Error(w, "Invalid request payload.", http.StatusBadRequest)
		return
	}

	_, err := db.Exec(`INSERT OR REPLACE INTO services (id, token, last_notification) VALUES (?, ?, ?)`,
		req.ServiceId, req.Token, time.Now().Format(time.RFC3339))
	if err != nil {
		http.Error(w, "Internal server error.", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
}

func getServices(w http.ResponseWriter, r *http.Request) {
	var req ServicesRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil || req.Token == "" {
		http.Error(w, "Invalid request payload.", http.StatusBadRequest)
		return
	}

	rows, err := db.Query(`SELECT id, last_notification FROM services WHERE token = ?`, req.Token)
	if err != nil {
		http.Error(w, "Internal server error.", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var services []ServiceStatus
	for rows.Next() {
		var service ServiceStatus
		var lastNotification sql.NullString
		if err := rows.Scan(&service.ServiceId, &lastNotification); err != nil {
			http.Error(w, "Internal server error.", http.StatusInternalServerError)
			return
		}
		if lastNotification.Valid {
			service.LastNotification, _ = time.Parse(time.RFC3339, lastNotification.String)
		}
		services = append(services, service)
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(services)
}

func main() {
	http.HandleFunc("/heartbeat", registerHeartbeat)
	http.HandleFunc("/services", getServices)

	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		panic(err)
	}
}