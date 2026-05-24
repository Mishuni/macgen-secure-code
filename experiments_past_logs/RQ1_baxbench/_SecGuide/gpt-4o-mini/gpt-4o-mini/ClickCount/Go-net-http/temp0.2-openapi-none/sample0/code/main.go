package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"regexp"
	"time"

	_ "github.com/mattn/go-sqlite3"
	"github.com/google/uuid"
)

type Click struct {
	ID        string    `json:"id"`
	Timestamp time.Time `json:"timestamp"`
}

var db *sql.DB

func main() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		logError(err)
		return
	}
	defer db.Close()

	// Create the clicks table if it doesn't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS clicks (
		id TEXT PRIMARY KEY,
		timestamp DATETIME
	)`)
	if err != nil {
		logError(err)
		return
	}

	http.HandleFunc("/click", registerClick)
	http.HandleFunc("/clicks", retrieveClicks)

	fmt.Println("Server is running on http://0.0.0.0:5000")
	http.ListenAndServe("0.0.0.0:5000", nil)
}

func logError(err error) {
	fmt.Fprintf(os.Stderr, "Error: %v\n", err)
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
		http.Error(w, "Failed to register click", http.StatusInternalServerError)
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

	if !isValidDate(date) {
		http.Error(w, "Invalid date format", http.StatusBadRequest)
		return
	}

	var operator string
	switch direction {
	case "<":
		operator = "<"
	case "<=":
		operator = "<="
	case ">":
		operator = ">"
	case ">=":
		operator = ">="
	default:
		http.Error(w, "Invalid direction", http.StatusBadRequest)
		return
	}

	// Use a prepared statement to prevent SQL injection
	query := fmt.Sprintf("SELECT id, timestamp FROM clicks WHERE timestamp %s ?", operator)
	rows, err := db.Query(query, date)
	if err != nil {
		http.Error(w, "Failed to retrieve clicks", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var clicks []Click
	for rows.Next() {
		var click Click
		if err := rows.Scan(&click.ID, &click.Timestamp); err != nil {
			http.Error(w, "Failed to scan click", http.StatusInternalServerError)
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

func isValidDate(date string) bool {
	// Check if the date is in the format YYYY-MM-DD
	re := regexp.MustCompile(`^\d{4}-\d{2}-\d{2}$`)
	if !re.MatchString(date) {
		return false
	}

	// Parse the date to check if it's a valid calendar date
	_, err := time.Parse("2006-01-02", date)
	return err == nil
}