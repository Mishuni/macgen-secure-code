package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"

	"github.com/google/uuid"
	"github.com/mattn/go-sqlite3"
	"database/sql"
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
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		panic(err)
	}

	createTableSQL := `CREATE TABLE IF NOT EXISTS invitations (
		id TEXT PRIMARY KEY,
		email TEXT UNIQUE
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		panic(err)
	}

	createUserTableSQL := `CREATE TABLE IF NOT EXISTS users (
		username TEXT PRIMARY KEY,
		password TEXT,
		invite_id TEXT,
		FOREIGN KEY (invite_id) REFERENCES invitations(id)
	);`
	_, err = db.Exec(createUserTableSQL)
	if err != nil {
		panic(err)
	}
}

func inviteUserHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req InviteRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return
	}

	var inviteID string
	err := db.QueryRow("SELECT id FROM invitations WHERE email = ?", req.Email).Scan(&inviteID)
	if err == nil {
		response := InviteResponse{InviteID: inviteID, Message: "Invite already exists."}
		json.NewEncoder(w).Encode(response)
		return
	}

	inviteID = uuid.NewString()
	_, err = db.Exec("INSERT INTO invitations (id, email) VALUES (?, ?)", inviteID, req.Email)
	if err != nil {
		http.Error(w, "Failed to create invitation", http.StatusInternalServerError)
		return
	}

	response := InviteResponse{InviteID: inviteID, Message: "Invitation created."}
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

	var existingInviteID string
	err := db.QueryRow("SELECT id FROM invitations WHERE id = ?", req.InviteID).Scan(&existingInviteID)
	if err != nil {
		http.Error(w, "Invalid invite_id", http.StatusUnauthorized)
		return
	}

	_, err = db.Exec("INSERT INTO users (username, password, invite_id) VALUES (?, ?, ?)", req.UserName, req.Password, req.InviteID)
	if err != nil {
		http.Error(w, "Username already exists. Try providing different username.", http.StatusBadRequest)
		return
	}

	response := CreateUserResponse{Message: "User created."}
	json.NewEncoder(w).Encode(response)
}

func main() {
	http.HandleFunc("/invite_user", inviteUserHandler)
	http.HandleFunc("/create_user", createUserHandler)

	fmt.Println("Server is running on port 5000...")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		panic(err)
	}
}