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

var db *sql.DB

func init() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}

	// Create tables if they don't exist
	createTables := `
	CREATE TABLE IF NOT EXISTS invitations (
		id TEXT PRIMARY KEY,
		email TEXT UNIQUE NOT NULL
	);
	CREATE TABLE IF NOT EXISTS users (
		id TEXT PRIMARY KEY,
		username TEXT UNIQUE NOT NULL,
		password TEXT NOT NULL
	);
	`
	_, err = db.Exec(createTables)
	if err != nil {
		log.Fatalf("Failed to create tables: %v", err)
	}
}

func main() {
	http.HandleFunc("/invite_user", inviteUserHandler)
	http.HandleFunc("/create_user", createUserHandler)

	log.Println("Server is running on 0.0.0.0:5000")
	log.Fatal(http.ListenAndServe("0.0.0.0:5000", nil))
}

func inviteUserHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var requestBody struct {
		Email string `json:"email"`
	}

	if err := json.NewDecoder(r.Body).Decode(&requestBody); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	if requestBody.Email == "" {
		http.Error(w, "Email is required", http.StatusBadRequest)
		return
	}

	// Check if an invitation already exists for the email
	var existingInviteID string
	err := db.QueryRow("SELECT id FROM invitations WHERE email = ?", requestBody.Email).Scan(&existingInviteID)
	if err == nil {
		// Invitation already exists
		response := map[string]string{
			"invite_id": existingInviteID,
			"message":   "Invitation already exists for this email",
		}
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(response)
		return
	} else if err != sql.ErrNoRows {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}

	// Create a new invitation
	inviteID := uuid.New().String()
	_, err = db.Exec("INSERT INTO invitations (id, email) VALUES (?, ?)", inviteID, requestBody.Email)
	if err != nil {
		http.Error(w, "Failed to create invitation", http.StatusInternalServerError)
		return
	}

	response := map[string]string{
		"invite_id": inviteID,
		"message":   "Invitation created successfully",
	}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func createUserHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var requestBody struct {
		InviteID string `json:"invite_id"`
		UserName string `json:"user_name"`
		Password string `json:"password"`
	}

	if err := json.NewDecoder(r.Body).Decode(&requestBody); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	if requestBody.InviteID == "" || requestBody.UserName == "" || requestBody.Password == "" {
		http.Error(w, "All fields are required", http.StatusBadRequest)
		return
	}

	// Validate the invitation ID
	var email string
	err := db.QueryRow("SELECT email FROM invitations WHERE id = ?", requestBody.InviteID).Scan(&email)
	if err == sql.ErrNoRows {
		http.Error(w, `{"message":"Invalid invite_id"}`, http.StatusUnauthorized)
		return
	} else if err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}

	// Check if the username already exists
	var existingUserID string
	err = db.QueryRow("SELECT id FROM users WHERE username = ?", requestBody.UserName).Scan(&existingUserID)
	if err == nil {
		http.Error(w, `{"message":"Username already exists. Try providing different username."}`, http.StatusBadRequest)
		return
	} else if err != sql.ErrNoRows {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}

	// Create the new user
	userID := uuid.New().String()
	_, err = db.Exec("INSERT INTO users (id, username, password) VALUES (?, ?, ?)", userID, requestBody.UserName, requestBody.Password)
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