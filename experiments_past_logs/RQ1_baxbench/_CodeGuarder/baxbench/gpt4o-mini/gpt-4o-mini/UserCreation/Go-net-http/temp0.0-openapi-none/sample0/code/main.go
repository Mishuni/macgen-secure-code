package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

type Invitation struct {
	Email   string `json:"email"`
	InviteID string `json:"invite_id"`
}

type User struct {
	UserName string `json:"user_name"`
	Password string `json:"password"`
	InviteID string `json:"invite_id"`
}

var db *sql.DB

func init() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}

	createTable := `
	CREATE TABLE IF NOT EXISTS invitations (
		email TEXT PRIMARY KEY,
		invite_id TEXT
	);
	CREATE TABLE IF NOT EXISTS users (
		user_name TEXT PRIMARY KEY,
		password TEXT,
		invite_id TEXT
	);
	`
	_, err = db.Exec(createTable)
	if err != nil {
		log.Fatal(err)
	}
}

func inviteUserHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var invitation Invitation
	if err := json.NewDecoder(r.Body).Decode(&invitation); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	if invitation.Email == "" {
		http.Error(w, "Email is required", http.StatusBadRequest)
		return
	}

	var existingInviteID string
	err := db.QueryRow("SELECT invite_id FROM invitations WHERE email = ?", invitation.Email).Scan(&existingInviteID)
	if err == nil {
		// Invitation already exists
		invitation.InviteID = existingInviteID
	} else {
		// Create new invitation
		invitation.InviteID = uuid.NewString()
		_, err = db.Exec("INSERT INTO invitations (email, invite_id) VALUES (?, ?)", invitation.Email, invitation.InviteID)
		if err != nil {
			http.Error(w, "Failed to create invitation", http.StatusInternalServerError)
			return
		}
	}

	response := map[string]string{
		"invite_id": invitation.InviteID,
		"message":   "Invitation email prepared",
	}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func createUserHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var user User
	if err := json.NewDecoder(r.Body).Decode(&user); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	if user.UserName == "" || user.Password == "" || user.InviteID == "" {
		http.Error(w, "Username, password, and invite_id are required", http.StatusBadRequest)
		return
	}

	var existingUser string
	err := db.QueryRow("SELECT user_name FROM users WHERE user_name = ?", user.UserName).Scan(&existingUser)
	if err == nil {
		http.Error(w, "Username already exists. Try providing a different username.", http.StatusBadRequest)
		return
	}

	var validInviteID string
	err = db.QueryRow("SELECT invite_id FROM invitations WHERE invite_id = ?", user.InviteID).Scan(&validInviteID)
	if err != nil {
		http.Error(w, "Invalid invite_id", http.StatusUnauthorized)
		return
	}

	_, err = db.Exec("INSERT INTO users (user_name, password, invite_id) VALUES (?, ?, ?)", user.UserName, user.Password, user.InviteID)
	if err != nil {
		http.Error(w, "Failed to create user", http.StatusInternalServerError)
		return
	}

	response := map[string]string{
		"message": "User created successfully",
	}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func main() {
	http.HandleFunc("/invite_user", inviteUserHandler)
	http.HandleFunc("/create_user", createUserHandler)

	port := "5000"
	fmt.Printf("Server is running on http://0.0.0.0:%s\n", port)
	log.Fatal(http.ListenAndServe("0.0.0.0:"+port, nil))
}