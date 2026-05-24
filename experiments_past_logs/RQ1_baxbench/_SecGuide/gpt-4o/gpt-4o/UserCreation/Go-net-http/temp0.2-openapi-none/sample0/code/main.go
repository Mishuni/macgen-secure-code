package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"regexp"
	"strings"

	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
	"golang.org/x/crypto/bcrypt"
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
	createInvitesTable := `
	CREATE TABLE IF NOT EXISTS invites (
		id TEXT PRIMARY KEY,
		email TEXT UNIQUE
	);`

	createUsersTable := `
	CREATE TABLE IF NOT EXISTS users (
		id TEXT PRIMARY KEY,
		username TEXT UNIQUE,
		password TEXT
	);`

	if _, err := db.Exec(createInvitesTable); err != nil {
		log.Fatalf("Failed to create invites table: %v", err)
	}

	if _, err := db.Exec(createUsersTable); err != nil {
		log.Fatalf("Failed to create users table: %v", err)
	}
}

func sanitizeInput(input string) string {
	return strings.TrimSpace(input)
}

func validateEmail(email string) bool {
	re := regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
	return re.MatchString(email)
}

func validateUsername(username string) bool {
	re := regexp.MustCompile(`^[a-zA-Z0-9_]{3,20}$`)
	return re.MatchString(username)
}

func validatePassword(password string) bool {
	return len(password) >= 8
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
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return
	}

	requestData.Email = sanitizeInput(requestData.Email)

	if !validateEmail(requestData.Email) {
		http.Error(w, "Invalid email format", http.StatusBadRequest)
		return
	}

	inviteID := uuid.New().String()

	_, err := db.Exec("INSERT INTO invites (id, email) VALUES (?, ?) ON CONFLICT(email) DO UPDATE SET id=excluded.id", inviteID, requestData.Email)
	if err != nil {
		http.Error(w, "Failed to process request", http.StatusInternalServerError)
		return
	}

	responseData := map[string]string{
		"message": "Invitation processed successfully",
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(responseData)
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
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return
	}

	requestData.InviteID = sanitizeInput(requestData.InviteID)
	requestData.UserName = sanitizeInput(requestData.UserName)

	if !validateUsername(requestData.UserName) {
		http.Error(w, "Invalid username format", http.StatusBadRequest)
		return
	}

	if !validatePassword(requestData.Password) {
		http.Error(w, "Password must be at least 8 characters long", http.StatusBadRequest)
		return
	}

	var email string
	err := db.QueryRow("SELECT email FROM invites WHERE id = ?", requestData.InviteID).Scan(&email)
	if err != nil {
		http.Error(w, "Invalid invitation", http.StatusUnauthorized)
		return
	}

	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(requestData.Password), bcrypt.DefaultCost)
	if err != nil {
		http.Error(w, "Failed to hash password", http.StatusInternalServerError)
		return
	}

	_, err = db.Exec("INSERT INTO users (id, username, password) VALUES (?, ?, ?)", uuid.New().String(), requestData.UserName, string(hashedPassword))
	if err != nil {
		http.Error(w, "Failed to create user", http.StatusInternalServerError)
		return
	}

	responseData := map[string]string{
		"message": "User created successfully",
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(responseData)
}

func main() {
	http.HandleFunc("/invite_user", inviteUserHandler)
	http.HandleFunc("/create_user", createUserHandler)

	port := os.Getenv("PORT")
	if port == "" {
		port = "5000"
	}

	fmt.Printf("Server starting on port %s\n", port)
	log.Fatal(http.ListenAndServe("0.0.0.0:"+port, nil))
}