package main

import (
	"encoding/json"
	"net/http"
	"os"

	"github.com/google/uuid"
	"github.com/mattn/go-sqlite3"
	_ "github.com/mattn/go-sqlite3"
)

type InviteRequest struct {
	Email string `json:"email"`
}

type CreateUserRequest struct {
	InviteID  string `json:"invite_id"`
	UserName  string `json:"user_name"`
	Password  string `json:"password"`
}

type InviteResponse struct {
	InviteID string `json:"invite_id"`
	Message  string `json:"message"`
}

type UserResponse struct {
	Message string `json:"message"`
}

var db *sql.DB

func init() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		panic(err)
	}

	// Create tables if they don't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS invitations (
		id TEXT PRIMARY KEY,
		email TEXT UNIQUE NOT NULL
	);`)
	if err != nil {
		panic(err)
	}

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS users (
		id TEXT PRIMARY KEY,
		username TEXT UNIQUE NOT NULL,
		password TEXT NOT NULL
	);`)
	if err != nil {
		panic(err)
	}
}

func inviteUser(w http.ResponseWriter, r *http.Request) {
	var req InviteRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil || req.Email == "" {
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	var inviteID string
	err := db.QueryRow("SELECT id FROM invitations WHERE email = ?", req.Email).Scan(&inviteID)
	if err != nil && err != sql.ErrNoRows {
		http.Error(w, "Database error", http.StatusInternalServerError)
		return
	}

	if inviteID == "" {
		inviteID = uuid.NewString()
		_, err = db.Exec("INSERT INTO invitations (id, email) VALUES (?, ?)", inviteID, req.Email)
		if err != nil {
			http.Error(w, "Database error", http.StatusInternalServerError)
			return
		}
	}

	response := InviteResponse{
		InviteID: inviteID,
		Message:  "Invitation created successfully",
	}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func createUser(w http.ResponseWriter, r *http.Request) {
	var req CreateUserRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil || req.InviteID == "" || req.UserName == "" || req.Password == "" {
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	var email string
	err := db.QueryRow("SELECT email FROM invitations WHERE id = ?", req.InviteID).Scan(&email)
	if err != nil {
		if err == sql.ErrNoRows {
			http.Error(w, "Invalid invite_id", http.StatusUnauthorized)
		} else {
			http.Error(w, "Database error", http.StatusInternalServerError)
		}
		return
	}

	_, err = db.Exec("INSERT INTO users (id, username, password) VALUES (?, ?, ?)", uuid.NewString(), req.UserName, req.Password)
	if err != nil {
		if sqliteErr, ok := err.(sqlite3.Error); ok && sqliteErr.Code == sqlite3.ErrConstraint {
			http.Error(w, "Username already exists. Try providing a different username.", http.StatusBadRequest)
		} else {
			http.Error(w, "Database error", http.StatusInternalServerError)
		}
		return
	}

	response := UserResponse{
		Message: "User created successfully",
	}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func main() {
	http.HandleFunc("/invite_user", inviteUser)
	http.HandleFunc("/create_user", createUser)
	http.ListenAndServe("0.0.0.0:5000", nil)
}