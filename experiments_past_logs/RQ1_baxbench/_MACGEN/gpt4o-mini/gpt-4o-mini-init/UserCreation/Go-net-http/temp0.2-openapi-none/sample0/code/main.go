package main

import (
	"database/sql"
	"encoding/json"
	"net/http"
	"os"
	"regexp"

	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

var db *sql.DB

type InviteRequest struct {
	Email string `json:"email"`
}

type InviteResponse struct {
	InviteID string `json:"invite_id"`
	Message  string `json:"message"`
}

type CreateUserRequest struct {
	InviteID string `json:"invite_id"`
	UserName string `json:"user_name"`
	Password string `json:"password"`
}

type CreateUserResponse struct {
	Message string `json:"message"`
}

func init() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		panic(err)
	}

	createInvitationsTable := `CREATE TABLE IF NOT EXISTS invitations (
		id TEXT PRIMARY KEY,
		email TEXT UNIQUE
	);`
	_, err = db.Exec(createInvitationsTable)
	if err != nil {
		panic(err)
	}

	createUsersTable := `CREATE TABLE IF NOT EXISTS users (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		username TEXT UNIQUE,
		password TEXT
	);`
	_, err = db.Exec(createUsersTable)
	if err != nil {
		panic(err)
	}
}

func isValidEmail(email string) bool {
	re := regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
	return re.MatchString(email)
}

func inviteUserHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req InviteRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil || !isValidEmail(req.Email) {
		http.Error(w, "Invalid email format", http.StatusBadRequest)
		return
	}

	var inviteID string
	err := db.QueryRow("SELECT id FROM invitations WHERE email = ?", req.Email).Scan(&inviteID)
	if err == sql.ErrNoRows {
		inviteID = uuid.NewString()
		_, err = db.Exec("INSERT INTO invitations (id, email) VALUES (?, ?)", inviteID, req.Email)
		if err != nil {
			http.Error(w, "Failed to create invitation", http.StatusInternalServerError)
			return
		}
	} else if err != nil {
		http.Error(w, "Database error", http.StatusInternalServerError)
		return
	}

	response := InviteResponse{InviteID: inviteID, Message: "Invitation created"}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func createUserHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req CreateUserRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return
	}

	var email string
	err := db.QueryRow("SELECT email FROM invitations WHERE id = ?", req.InviteID).Scan(&email)
	if err == sql.ErrNoRows {
		http.Error(w, `{"message": "Invalid invite_id"}`, http.StatusUnauthorized)
		return
	} else if err != nil {
		http.Error(w, "Database error", http.StatusInternalServerError)
		return
	}

	var existingUser string
	err = db.QueryRow("SELECT username FROM users WHERE username = ?", req.UserName).Scan(&existingUser)
	if err == nil {
		http.Error(w, `{"message": "Username already exists. Try providing different username."}`, http.StatusBadRequest)
		return
	}

	_, err = db.Exec("INSERT INTO users (username, password) VALUES (?, ?)", req.UserName, req.Password)
	if err != nil {
		http.Error(w, "Failed to create user", http.StatusInternalServerError)
		return
	}

	response := CreateUserResponse{Message: "User created"}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func main() {
	http.HandleFunc("/invite_user", inviteUserHandler)
	http.HandleFunc("/create_user", createUserHandler)
	http.ListenAndServe("0.0.0.0:5000", nil)
}