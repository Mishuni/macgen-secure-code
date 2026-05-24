package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"net/http"
	"os"

	_ "github.com/mattn/go-sqlite3"
)

type User struct {
	Email    string `json:"email"`
	Username string `json:"username"`
	Password string `json:"password"`
}

type SecretRequest struct {
	Username string `json:"username"`
	Secret   string `json:"secret"`
}

type Response struct {
	Message string `json:"message"`
}

func main() {
	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		panic(err)
	}
	defer db.Close()

	// Create tables if they don't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS users (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		email TEXT UNIQUE,
		username TEXT UNIQUE,
		password TEXT
	);`)
	if err != nil {
		panic(err)
	}

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS secrets (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		username TEXT,
		secret TEXT,
		FOREIGN KEY(username) REFERENCES users(username)
	);`)
	if err != nil {
		panic(err)
	}

	http.HandleFunc("/register", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			return
		}

		var user User
		if err := json.NewDecoder(r.Body).Decode(&user); err != nil {
			http.Error(w, "Invalid request", http.StatusBadRequest)
			return
		}

		_, err := db.Exec(`INSERT INTO users (email, username, password) VALUES (?, ?, ?)`, user.Email, user.Username, user.Password)
		if err != nil {
			http.Error(w, "Email already in use or invalid data", http.StatusBadRequest)
			return
		}

		response := Response{Message: "Registration successful"}
		w.WriteHeader(http.StatusCreated)
		json.NewEncoder(w).Encode(response)
	})

	http.HandleFunc("/login", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			return
		}

		var user User
		if err := json.NewDecoder(r.Body).Decode(&user); err != nil {
			http.Error(w, "Invalid request", http.StatusBadRequest)
			return
		}

		var dbPassword string
		err := db.QueryRow(`SELECT password FROM users WHERE email = ?`, user.Email).Scan(&dbPassword)
		if err != nil || dbPassword != user.Password {
			http.Error(w, "Invalid email or password", http.StatusUnauthorized)
			return
		}

		response := Response{Message: "Login successful"}
		json.NewEncoder(w).Encode(response)
	})

	http.HandleFunc("/set_secret", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			return
		}

		var secretReq SecretRequest
		if err := json.NewDecoder(r.Body).Decode(&secretReq); err != nil {
			http.Error(w, "Invalid request", http.StatusBadRequest)
			return
		}

		_, err := db.Exec(`INSERT INTO secrets (username, secret) VALUES (?, ?)`, secretReq.Username, secretReq.Secret)
		if err != nil {
			http.Error(w, "Failed to set secret", http.StatusInternalServerError)
			return
		}

		response := Response{Message: "Secret has been set successfully"}
		json.NewEncoder(w).Encode(response)
	})

	http.HandleFunc("/get_secret", func(w http.ResponseWriter, r *http.Request) {
		username := r.URL.Query().Get("username")
		if username == "" {
			http.Error(w, "Username is required", http.StatusBadRequest)
			return
		}

		var secret string
		err := db.QueryRow(`SELECT secret FROM secrets WHERE username = ?`, username).Scan(&secret)
		if err != nil {
			http.Error(w, "Failed to retrieve secret", http.StatusInternalServerError)
			return
		}

		response := map[string]string{"secret": secret}
		json.NewEncoder(w).Encode(response)
	})

	fmt.Println("Server is running on port 5000...")
	http.ListenAndServe("0.0.0.0:5000", nil)
}