package main

import (
	"database/sql"
	"encoding/json"
	"net/http"
	"os"

	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

var db *sql.DB

type User struct {
	Email    string `json:"email"`
	Username string `json:"username"`
	Password string `json:"password"`
}

type Secret struct {
	Username string `json:"username"`
	Secret   string `json:"secret"`
}

type ResponseMessage struct {
	Message string `json:"message"`
}

func main() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		http.Error(nil, "Database connection failed", http.StatusInternalServerError)
		return
	}
	defer db.Close()

	// Create tables if they don't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, email TEXT, username TEXT, password TEXT)`)
	if err != nil {
		http.Error(nil, "Failed to create users table", http.StatusInternalServerError)
		return
	}
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS secrets (id TEXT PRIMARY KEY, username TEXT, secret TEXT)`)
	if err != nil {
		http.Error(nil, "Failed to create secrets table", http.StatusInternalServerError)
		return
	}

	http.HandleFunc("/register", registerHandler)
	http.HandleFunc("/login", loginHandler)
	http.HandleFunc("/set_secret", setSecretHandler)
	http.HandleFunc("/get_secret", getSecretHandler)

	http.ListenAndServe("0.0.0.0:5000", nil)
}

func registerHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var user User
	if err := json.NewDecoder(r.Body).Decode(&user); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	id := uuid.New().String()
	_, err := db.Exec("INSERT INTO users (id, email, username, password) VALUES (?, ?, ?, ?)", id, user.Email, user.Username, user.Password)
	if err != nil {
		http.Error(w, "Email already in use or invalid data", http.StatusBadRequest)
		return
	}

	response := ResponseMessage{Message: "Registration successful"}
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(response)
}

func loginHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var user User
	if err := json.NewDecoder(r.Body).Decode(&user); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	var dbUser User
	err := db.QueryRow("SELECT email, username, password FROM users WHERE email = ?", user.Email).Scan(&dbUser.Email, &dbUser.Username, &dbUser.Password)
	if err != nil || dbUser.Password != user.Password {
		http.Error(w, "Invalid email or password", http.StatusUnauthorized)
		return
	}

	response := ResponseMessage{Message: "Login successful"}
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(response)
}

func setSecretHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var secret Secret
	if err := json.NewDecoder(r.Body).Decode(&secret); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	id := uuid.New().String()
	_, err := db.Exec("INSERT INTO secrets (id, username, secret) VALUES (?, ?, ?)", id, secret.Username, secret.Secret)
	if err != nil {
		http.Error(w, "Failed to set secret", http.StatusInternalServerError)
		return
	}

	response := ResponseMessage{Message: "Secret has been set successfully"}
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(response)
}

func getSecretHandler(w http.ResponseWriter, r *http.Request) {
	username := r.URL.Query().Get("username")
	if username == "" {
		http.Error(w, "Username is required", http.StatusBadRequest)
		return
	}

	var secret string
	err := db.QueryRow("SELECT secret FROM secrets WHERE username = ?", username).Scan(&secret)
	if err != nil {
		http.Error(w, "Failed to retrieve secret", http.StatusInternalServerError)
		return
	}

	response := map[string]string{"secret": secret}
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(response)
}