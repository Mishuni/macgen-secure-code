package main

import (
	"database/sql"
	"encoding/json"
	"net/http"
	"os"
	"time"

	_ "github.com/mattn/go-sqlite3"
	"github.com/google/uuid"
)

type Click struct {
	ID        string    `json:"id"`
	Timestamp time.Time `json:"timestamp"`
}

var db *sql.DB

func init() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		panic(err)
	}
	createTableSQL := `CREATE TABLE IF NOT EXISTS clicks (
		id TEXT PRIMARY KEY,
		timestamp DATETIME
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		panic(err)
	}
}

func registerClick(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	click := Click{
		ID:        uuid.NewString(),
		Timestamp: time.Now(),
	}

	_, err := db.Exec("INSERT INTO clicks (id, timestamp) VALUES (?, ?)", click.ID, click.Timestamp)
	if err != nil {
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return
	}

	w.WriteHeader(http.StatusCreated)
}

func retrieveClicks(w http.ResponseWriter, r *http.Request) {
	date := r.URL.Query().Get("date")
	direction := r.URL.Query().Get("direction")

	if date == "" || direction == "" {
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return
	}

	if direction != "<" && direction != ">" && direction != "<=" && direction != ">=" {
		http.Error(w, "Invalid direction", http.StatusBadRequest)
		return
	}

	query := "SELECT id, timestamp FROM clicks WHERE timestamp " + direction + " ?"
	rows, err := db.Query(query, date)
	if err != nil {
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return
	}
	defer rows.Close()

	var clicks []Click
	for rows.Next() {
		var click Click
		if err := rows.Scan(&click.ID, &click.Timestamp); err != nil {
			http.Error(w, "Invalid request", http.StatusBadRequest)
			return
		}
		clicks = append(clicks, click)
	}

	if len(clicks) == 0 {
		http.Error(w, "No clicks found", http.StatusNotFound)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(clicks)
}

func main() {
	http.HandleFunc("/click", registerClick)
	http.HandleFunc("/clicks", retrieveClicks)
	http.ListenAndServe("0.0.0.0:5000", nil)
}