package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"regexp"

	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

var db *sql.DB

func init() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to open database: %v", err)
	}

	createTables()
}

func createTables() {
	createInviteTable := `
	CREATE TABLE IF NOT EXISTS invites (
		id TEXT PRIMARY KEY,
		email TEXT UNIQUE NOT NULL
	);`

	createUserTable := `
	CREATE TABLE IF NOT EXISTS users (
		id TEXT PRIMARY KEY,
		username TEXT UNIQUE NOT NULL,
		password TEXT NOT NULL
	);`

	if _, err := db.Exec(createInviteTable); err != nil {
		log.Fatalf("Failed to create invites table: %v", err)
	}

	if _, err := db.Exec(createUserTable); err != nil {
		log.Fatalf("Failed to create users table: %v", err)
	}
}

func inviteUserHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var requestData struct {
		Email string `json:"email"`
	}

	if err := json.NewDecoder(r.Body).Decode(&requestData); err != nil {
		http.Error(w, "Invalid request payload", http.StatusBadRequest)
		return
	}

	if !isValidEmail(requestData.Email) {
		http.Error(w, "Invalid email format", http.StatusBadRequest)
		return
	}

	inviteID, err := createOrRetrieveInvite(requestData.Email)
	if err != nil {
		http.Error(w, "Failed to create or retrieve invite", http.StatusInternalServerError)
		return
	}

	responseData := map[string]string{
		"invite_id": inviteID,
		"message":   "Invitation created successfully",
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(responseData)
}

func createOrRetrieveInvite(email string) (string, error) {
	var inviteID string
	err := db.QueryRow("SELECT id FROM invites WHERE email = ?", email).Scan(&inviteID)
	if err == sql.ErrNoRows {
		inviteID = uuid.New().String()
		_, err = db.Exec("INSERT INTO invites (id, email) VALUES (?, ?)", inviteID, email)
		if err != nil {
			return "", err
		}
	} else if err != nil {
		return "", err
	}
	return inviteID, nil
}

func createUserHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var requestData struct {
		InviteID string `json:"invite_id"`
		UserName string `json:"user_name"`
		Password string `json:"password"`
	}

	if err := json.NewDecoder(r.Body).Decode(&requestData); err != nil {
		http.Error(w, "Invalid request payload", http.StatusBadRequest)
		return
	}

	if !isValidInvite(requestData.InviteID) {
		http.Error(w, "Invalid invite_id", http.StatusUnauthorized)
		return
	}

	if err := createUser(requestData.UserName, requestData.Password); err != nil {
		http.Error(w, "Username already exists. Try providing different username.", http.StatusBadRequest)
		return
	}

	responseData := map[string]string{
		"message": "User created successfully",
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(responseData)
}

func isValidInvite(inviteID string) bool {
	var id string
	err := db.QueryRow("SELECT id FROM invites WHERE id = ?", inviteID).Scan(&id)
	return err == nil
}

func createUser(username, password string) error {
	_, err := db.Exec("INSERT INTO users (id, username, password) VALUES (?, ?, ?)", uuid.New().String(), username, password)
	return err
}

func isValidEmail(email string) bool {
	re := regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
	return re.MatchString(email)
}

func main() {
	http.HandleFunc("/invite_user", inviteUserHandler)
	http.HandleFunc("/create_user", createUserHandler)

	port := "5000"
	fmt.Printf("Server starting on port %s\n", port)
	log.Fatal(http.ListenAndServe("0.0.0.0:"+port, nil))
}