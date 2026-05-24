package main

import (
	"database/sql"
	"encoding/json"
	"errors"
	"log"
	"net/http"
	"os"

	"github.com/golang-jwt/jwt/v5"
	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

var db *sql.DB
var appSecret string

type User struct {
	Email    string `json:"email"`
	Username string `json:"username"`
	Password string `json:"password"`
}

type LoginRequest struct {
	Email    string `json:"email"`
	Password string `json:"password"`
}

type SecretRequest struct {
	Username string `json:"username"`
	Secret   string `json:"secret"`
}

type ErrorResponse struct {
	Message string `json:"message"`
}

type SuccessResponse struct {
	Message string `json:"message"`
}

type TokenResponse struct {
	Token   string `json:"token"`
	Message string `json:"message"`
}

type SecretResponse struct {
	Secret string `json:"secret"`
}

func initDB() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}

	_, err = db.Exec(`
		CREATE TABLE IF NOT EXISTS users (
			id TEXT PRIMARY KEY,
			email TEXT UNIQUE NOT NULL,
			username TEXT UNIQUE NOT NULL,
			password TEXT NOT NULL
		);
		CREATE TABLE IF NOT EXISTS secrets (
			id TEXT PRIMARY KEY,
			username TEXT NOT NULL,
			secret TEXT NOT NULL,
			FOREIGN KEY (username) REFERENCES users(username)
		);
	`)
	if err != nil {
		log.Fatalf("Failed to initialize database: %v", err)
	}
}

func registerHandler(w http.ResponseWriter, r *http.Request) {
	var user User
	if err := json.NewDecoder(r.Body).Decode(&user); err != nil {
		http.Error(w, `{"message":"Invalid request body"}`, http.StatusBadRequest)
		return
	}

	if user.Email == "" || user.Username == "" || user.Password == "" {
		http.Error(w, `{"message":"Missing required fields"}`, http.StatusBadRequest)
		return
	}

	_, err := db.Exec("INSERT INTO users (id, email, username, password) VALUES (?, ?, ?, ?)",
		uuid.New().String(), user.Email, user.Username, user.Password)
	if err != nil {
		http.Error(w, `{"message":"Email or username already in use"}`, http.StatusBadRequest)
		return
	}

	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(SuccessResponse{Message: "Registration successful"})
}

func loginHandler(w http.ResponseWriter, r *http.Request) {
	var loginReq LoginRequest
	if err := json.NewDecoder(r.Body).Decode(&loginReq); err != nil {
		http.Error(w, `{"message":"Invalid request body"}`, http.StatusBadRequest)
		return
	}

	if loginReq.Email == "" || loginReq.Password == "" {
		http.Error(w, `{"message":"Missing required fields"}`, http.StatusBadRequest)
		return
	}

	var username string
	err := db.QueryRow("SELECT username FROM users WHERE email = ? AND password = ?", loginReq.Email, loginReq.Password).Scan(&username)
	if err != nil {
		http.Error(w, `{"message":"Invalid email or password"}`, http.StatusUnauthorized)
		return
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
		"username": username,
	})
	tokenString, err := token.SignedString([]byte(appSecret))
	if err != nil {
		http.Error(w, `{"message":"Failed to generate token"}`, http.StatusInternalServerError)
		return
	}

	json.NewEncoder(w).Encode(TokenResponse{Token: tokenString, Message: "Login successful"})
}

func setSecretHandler(w http.ResponseWriter, r *http.Request) {
	var secretReq SecretRequest
	if err := json.NewDecoder(r.Body).Decode(&secretReq); err != nil {
		http.Error(w, `{"message":"Invalid request body"}`, http.StatusBadRequest)
		return
	}

	if secretReq.Username == "" || secretReq.Secret == "" {
		http.Error(w, `{"message":"Missing required fields"}`, http.StatusBadRequest)
		return
	}

	_, err := db.Exec("INSERT INTO secrets (id, username, secret) VALUES (?, ?, ?) ON CONFLICT(username) DO UPDATE SET secret = ?",
		uuid.New().String(), secretReq.Username, secretReq.Secret, secretReq.Secret)
	if err != nil {
		http.Error(w, `{"message":"Failed to set secret"}`, http.StatusInternalServerError)
		return
	}

	json.NewEncoder(w).Encode(SuccessResponse{Message: "Secret has been set successfully"})
}

func getSecretHandler(w http.ResponseWriter, r *http.Request) {
	username := r.URL.Query().Get("username")
	if username == "" {
		http.Error(w, `{"message":"Missing username parameter"}`, http.StatusBadRequest)
		return
	}

	var secret string
	err := db.QueryRow("SELECT secret FROM secrets WHERE username = ?", username).Scan(&secret)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			http.Error(w, `{"message":"Secret not found"}`, http.StatusNotFound)
		} else {
			http.Error(w, `{"message":"Failed to retrieve secret"}`, http.StatusInternalServerError)
		}
		return
	}

	json.NewEncoder(w).Encode(SecretResponse{Secret: secret})
}

func main() {
	appSecret = os.Getenv("APP_SECRET")
	if appSecret == "" {
		log.Fatal("APP_SECRET environment variable is required")
	}

	initDB()
	defer db.Close()

	http.HandleFunc("/register", registerHandler)
	http.HandleFunc("/login", loginHandler)
	http.HandleFunc("/set_secret", setSecretHandler)
	http.HandleFunc("/get_secret", getSecretHandler)

	log.Println("Server is running on 0.0.0.0:5000")
	log.Fatal(http.ListenAndServe("0.0.0.0:5000", nil))
}