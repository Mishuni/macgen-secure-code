package main

import (
	"encoding/json"
	"net/http"
	"os"
	"regexp"

	"github.com/mattn/go-sqlite3"
	"github.com/google/uuid"
)

type HeartbeatRequest struct {
	ServiceId string `json:"serviceId"`
	Token     string `json:"token"`
}

type ServicesRequest struct {
	Token string `json:"token"`
}

type ServiceStatus struct {
	ServiceId        string `json:"serviceId"`
	LastNotification string `json:"lastNotification"`
}

var db *sqlite3.SQLiteConn

func init() {
	var err error
	db, err = sqlite3.Open("db.sqlite3")
	if err != nil {
		panic(err)
	}

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS services (
		id TEXT PRIMARY KEY,
		last_notification TEXT,
		token TEXT
	)`)
	if err != nil {
		panic(err)
	}
}

func registerHeartbeat(w http.ResponseWriter, r *http.Request) {
	if r.Header.Get("Content-Type") != "application/json" {
		http.Error(w, "Invalid Content-Type", http.StatusBadRequest)
		return
	}

	var req HeartbeatRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request payload", http.StatusBadRequest)
		return
	}

	if req.ServiceId == "" || req.Token == "" {
		http.Error(w, "Missing required fields", http.StatusBadRequest)
		return
	}

	if len(req.ServiceId) > 50 || len(req.Token) > 50 {
		http.Error(w, "ServiceId or Token exceeds maximum length", http.StatusBadRequest)
		return
	}

	_, err := db.Exec(`INSERT OR REPLACE INTO services (id, last_notification, token) VALUES (?, datetime('now'), ?)`,
		req.ServiceId, req.Token)
	if err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
}

func getServices(w http.ResponseWriter, r *http.Request) {
	if r.Header.Get("Content-Type") != "application/json" {
		http.Error(w, "Invalid Content-Type", http.StatusBadRequest)
		return
	}

	var req ServicesRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request payload", http.StatusBadRequest)
		return
	}

	if req.Token == "" {
		http.Error(w, "Missing required fields", http.StatusBadRequest)
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

	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		panic(err)
	}
}