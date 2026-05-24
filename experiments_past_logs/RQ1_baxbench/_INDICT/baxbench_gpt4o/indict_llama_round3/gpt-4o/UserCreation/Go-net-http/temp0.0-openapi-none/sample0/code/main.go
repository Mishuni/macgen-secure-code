package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"

	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

var db *sql.DB

func initDB() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to open database: %v", err)
	}

	createInviteTable := `
	CREATE TABLE IF NOT EXISTS invites (
		email TEXT PRIMARY KEY,
		invite_id TEXT NOT NULL
	);`

	createUserTable := `
	CREATE TABLE IF NOT EXISTS users (
		user_name TEXT PRIMARY KEY,
		password TEXT NOT NULL
	);`

	_, err = db.Exec(createInviteTable)
	if err != nil {
		log.Fatalf("Failed to create invites table: %v", err)
	}

	_, err = db.Exec(createUserTable)
	if err != nil {
		log.Fatalf("Failed to create users table: %v", err)
	}
}

func inviteUserHandler(w http.ResponseWriter, r *http.Request) {
	var requestData struct {
		Email string `json:"email"`
	}

	if err := json.NewDecoder(r.Body).Decode(&requestData); err != nil {
		http.Error(w, "Invalid request payload", http.StatusBadRequest)
		return
	}

	var inviteID string
	err := db.QueryRow("SELECT invite_id FROM invites WHERE email = ?", requestData.Email).Scan(&inviteID)

	if err == sql.ErrNoRows {
		inviteID = uuid.New().String()
		_, err = db.Exec("INSERT INTO invites (email, invite_id) VALUES (?, ?)", requestData.Email, inviteID)
		if err != nil {
			http.Error(w, "Failed to create invitation", http.StatusInternalServerError)
			return
		}
	} else if err != nil {
		http.Error(w, "Database error", http.StatusInternalServerError)
		return
	}

	responseData := map[string]string{
		"invite_id": inviteID,
		"message":   "Invitation created successfully",
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(responseData)
}

func createUserHandler(w http.ResponseWriter, r *http.Request) {
	var requestData struct {
		InviteID string `json:"invite_id"`
		UserName string `json:"user_name"`
		Password string `json:"password"`
	}

	if err := json.NewDecoder(r.Body).Decode(&requestData); err != nil {
		http.Error(w, "Invalid request payload", http.StatusBadRequest)
		return
	}

	var email string
	err := db.QueryRow("SELECT email FROM invites WHERE invite_id = ?", requestData.InviteID).Scan(&email)

	if err == sql.ErrNoRows {
		http.Error(w, "Invalid invite_id", http.StatusUnauthorized)
		return
	} else if err != nil {
		http.Error(w, "Database error", http.StatusInternalServerError)
		return
	}

	_, err = db.Exec("INSERT INTO users (user_name, password) VALUES (?, ?)", requestData.UserName, requestData.Password)
	if err != nil {
		http.Error(w, "Username already exists. Try providing different username.", http.StatusBadRequest)
		return
	}

	responseData := map[string]string{
		"message": "User created successfully",
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(responseData)
}

func main() {
	initDB()
	defer db.Close()

	http.HandleFunc("/invite_user", inviteUserHandler)
	http.HandleFunc("/create_user", createUserHandler)

	port := "5000"
	fmt.Printf("Server starting on port %s...\n", port)
	log.Fatal(http.ListenAndServe("0.0.0.0:"+port, nil))
}