package main

import (
	"database/sql"
	"encoding/json"
	"net/http"
	"os"

	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

type User struct {
	ID       string `json:"id"`
	Email    string `json:"email"`
	Password string `json:"password"`
	Name     string `json:"name"`
}

type LoginRequest struct {
	Email    string `json:"email"`
	Password string `json:"password"`
}

type RegisterRequest struct {
	Email    string `json:"email"`
	Password string `json:"password"`
	Name     string `json:"name"`
}

type Response struct {
	Message string `json:"message"`
	Token   string `json:"token,omitempty"`
}

func main() {
	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		panic(err)
	}
	defer db.Close()

	// Create users table if it doesn't exist
	createTableSQL := `CREATE TABLE IF NOT EXISTS users (
		id TEXT PRIMARY KEY,
		email TEXT UNIQUE,
		password TEXT,
		name TEXT
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		panic(err)
	}

	http.HandleFunc("/login", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			return
		}

		var loginReq LoginRequest
		if err := json.NewDecoder(r.Body).Decode(&loginReq); err != nil {
			http.Error(w, "Bad request", http.StatusBadRequest)
			return
		}

		var user User
		err := db.QueryRow("SELECT id, email FROM users WHERE email = ? AND password = ?", loginReq.Email, loginReq.Password).Scan(&user.ID, &user.Email)
		if err != nil {
			http.Error(w, `{"message": "Invalid email or password"}`, http.StatusUnauthorized)
			return
		}

		response := Response{Message: "Login successful", Token: "jwt-token-abc123"}
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(response)
	})

	http.HandleFunc("/register", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			return
		}

		var registerReq RegisterRequest
		if err := json.NewDecoder(r.Body).Decode(&registerReq); err != nil {
			http.Error(w, "Bad request", http.StatusBadRequest)
			return
		}

		id := uuid.New().String()
		_, err := db.Exec("INSERT INTO users (id, email, password, name) VALUES (?, ?, ?, ?)", id, registerReq.Email, registerReq.Password, registerReq.Name)
		if err != nil {
			http.Error(w, `{"message": "Email already in use or invalid data"}`, http.StatusBadRequest)
			return
		}

		response := Response{Message: "Registration successful"}
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusCreated)
		json.NewEncoder(w).Encode(response)
	})

	http.ListenAndServe("0.0.0.0:5000", nil)
}