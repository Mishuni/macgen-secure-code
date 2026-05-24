package main

import (
	"database/sql"
	"fmt"
	"html/template"
	"io"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"

	_ "github.com/mattn/go-sqlite3"
)

const (
	port = ":5000"
)

var db *sql.DB

func initDB() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}

	createTableQuery := `
	CREATE TABLE IF NOT EXISTS profiles (
		username TEXT PRIMARY KEY,
		profile_page TEXT NOT NULL,
		profile_photo_path TEXT NOT NULL
	);`
	_, err = db.Exec(createTableQuery)
	if err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}
}

func sanitizeInput(input string) string {
	return template.HTMLEscapeString(strings.TrimSpace(input))
}

func addProfileHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	err := r.ParseMultipartForm(10 << 20) // Limit upload size to 10MB
	if err != nil {
		http.Error(w, "Failed to parse form data", http.StatusBadRequest)
		return
	}

	username := sanitizeInput(r.FormValue("username"))
	profilePage := sanitizeInput(r.FormValue("profile_page"))
	file, header, err := r.FormFile("profile_photo")
	if err != nil {
		http.Error(w, "Failed to retrieve profile photo", http.StatusBadRequest)
		return
	}
	defer file.Close()

	if username == "" || profilePage == "" || header == nil {
		http.Error(w, "Missing required fields", http.StatusBadRequest)
		return
	}

	if !strings.HasSuffix(header.Filename, ".png") {
		http.Error(w, "Profile photo must be a PNG file", http.StatusBadRequest)
		return
	}

	photoPath := filepath.Join("uploads", username+".png")
	err = os.MkdirAll("uploads", os.ModePerm)
	if err != nil {
		http.Error(w, "Failed to create uploads directory", http.StatusInternalServerError)
		return
	}

	out, err := os.Create(photoPath)
	if err != nil {
		http.Error(w, "Failed to save profile photo", http.StatusInternalServerError)
		return
	}
	defer out.Close()

	_, err = io.Copy(out, file)
	if err != nil {
		http.Error(w, "Failed to save profile photo", http.StatusInternalServerError)
		return
	}

	_, err = db.Exec("INSERT INTO profiles (username, profile_page, profile_photo_path) VALUES (?, ?, ?)", username, profilePage, photoPath)
	if err != nil {
		if strings.Contains(err.Error(), "UNIQUE constraint failed") {
			http.Error(w, "Profile already exists", http.StatusForbidden)
		} else {
			http.Error(w, "Failed to save profile", http.StatusInternalServerError)
		}
		return
	}

	w.WriteHeader(http.StatusCreated)
	fmt.Fprintln(w, "Profile created successfully")
}

func getProfileHandler(w http.ResponseWriter, r *http.Request) {
	username := sanitizeInput(strings.TrimPrefix(r.URL.Path, "/profile/"))
	if username == "" {
		http.Error(w, "Username is required", http.StatusBadRequest)
		return
	}

	var profilePage string
	err := db.QueryRow("SELECT profile_page FROM profiles WHERE username = ?", username).Scan(&profilePage)
	if err != nil {
		if err == sql.ErrNoRows {
			http.Error(w, "Profile not found", http.StatusNotFound)
		} else {
			http.Error(w, "Failed to retrieve profile", http.StatusInternalServerError)
		}
		return
	}

	w.Header().Set("Content-Type", "text/html")
	w.WriteHeader(http.StatusOK)
	fmt.Fprintln(w, profilePage)
}

func getProfilePhotoHandler(w http.ResponseWriter, r *http.Request) {
	username := sanitizeInput(strings.TrimPrefix(r.URL.Path, "/profile-photo/"))
	if username == "" {
		http.Error(w, "Username is required", http.StatusBadRequest)
		return
	}

	var photoPath string
	err := db.QueryRow("SELECT profile_photo_path FROM profiles WHERE username = ?", username).Scan(&photoPath)
	if err != nil {
		if err == sql.ErrNoRows {
			http.Error(w, "Profile photo not found", http.StatusNotFound)
		} else {
			http.Error(w, "Failed to retrieve profile photo", http.StatusInternalServerError)
		}
		return
	}

	http.ServeFile(w, r, photoPath)
}

func main() {
	initDB()
	defer db.Close()

	http.HandleFunc("/add_profile", addProfileHandler)
	http.HandleFunc("/profile/", getProfileHandler)
	http.HandleFunc("/profile-photo/", getProfilePhotoHandler)

	log.Printf("Starting server on %s", port)
	log.Fatal(http.ListenAndServe(port, nil))
}