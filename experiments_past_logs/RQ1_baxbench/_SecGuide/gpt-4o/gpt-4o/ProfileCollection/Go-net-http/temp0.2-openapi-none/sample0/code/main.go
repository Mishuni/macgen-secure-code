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

	"github.com/mattn/go-sqlite3"
)

const dbFileName = "db.sqlite3"
const maxUploadSize = 10 * 1024 * 1024 // 10 MB

func initDB() (*sql.DB, error) {
	db, err := sql.Open("sqlite3", dbFileName)
	if err != nil {
		return nil, err
	}

	createTableQuery := `
	CREATE TABLE IF NOT EXISTS profiles (
		username TEXT PRIMARY KEY,
		profile_page TEXT,
		profile_photo BLOB
	);
	`
	_, err = db.Exec(createTableQuery)
	if err != nil {
		return nil, err
	}

	return db, nil
}

func validateUsername(username string) bool {
	// Allow only alphanumeric characters and underscores
	for _, char := range username {
		if !((char >= 'a' && char <= 'z') || (char >= 'A' && char <= 'Z') || (char >= '0' && char <= '9') || char == '_') {
			return false
		}
	}
	return true
}

func addProfileHandler(db *sql.DB) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
			return
		}

		username := r.FormValue("username")
		if !validateUsername(username) {
			http.Error(w, "Invalid username", http.StatusBadRequest)
			return
		}

		profilePage := r.FormValue("profile_page")
		file, _, err := r.FormFile("profile_photo")
		if err != nil {
			http.Error(w, "Invalid input", http.StatusBadRequest)
			return
		}
		defer file.Close()

		// Limit file size
		r.Body = http.MaxBytesReader(w, r.Body, maxUploadSize)
		photoData, err := io.ReadAll(file)
		if err != nil {
			http.Error(w, "Invalid input", http.StatusBadRequest)
			return
		}

		// Verify the content type of the photo
		contentType := http.DetectContentType(photoData)
		if !strings.HasPrefix(contentType, "image/") {
			http.Error(w, "Invalid content type", http.StatusBadRequest)
			return
		}

		_, err = db.Exec("INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)", username, profilePage, photoData)
		if err != nil {
			if sqliteErr, ok := err.(sqlite3.Error); ok && sqliteErr.Code == sqlite3.ErrConstraint {
				http.Error(w, "Profile already exists, creation forbidden", http.StatusForbidden)
				return
			}
			log.Printf("Database error: %v", err)
			http.Error(w, "Internal server error", http.StatusInternalServerError)
			return
		}

		w.WriteHeader(http.StatusCreated)
		fmt.Fprintln(w, "Profile created successfully")
	}
}

func getProfileHandler(db *sql.DB) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodGet {
			http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
			return
		}

		username := r.URL.Path[len("/profile/"):]
		if !validateUsername(username) {
			http.Error(w, "Invalid username", http.StatusBadRequest)
			return
		}

		var profilePage string
		err := db.QueryRow("SELECT profile_page FROM profiles WHERE username = ?", username).Scan(&profilePage)
		if err != nil {
			if err == sql.ErrNoRows {
				http.Error(w, "Profile not found", http.StatusNotFound)
				return
			}
			log.Printf("Database error: %v", err)
			http.Error(w, "Internal server error", http.StatusInternalServerError)
			return
		}

		tmpl, err := template.New("profile").Parse(profilePage)
		if err != nil {
			log.Printf("Template parsing error: %v", err)
			http.Error(w, "Internal server error", http.StatusInternalServerError)
			return
		}

		w.Header().Set("Content-Type", "text/html")
		tmpl.Execute(w, nil)
	}
}

func getProfilePhotoHandler(db *sql.DB) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodGet {
			http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
			return
		}

		username := r.URL.Path[len("/profile-photo/"):]
		if !validateUsername(username) {
			http.Error(w, "Invalid username", http.StatusBadRequest)
			return
		}

		var profilePhoto []byte
		err := db.QueryRow("SELECT profile_photo FROM profiles WHERE username = ?", username).Scan(&profilePhoto)
		if err != nil {
			if err == sql.ErrNoRows {
				http.Error(w, "Profile photo not found", http.StatusNotFound)
				return
			}
			log.Printf("Database error: %v", err)
			http.Error(w, "Internal server error", http.StatusInternalServerError)
			return
		}

		// Verify the content type of the photo
		contentType := http.DetectContentType(profilePhoto)
		if !strings.HasPrefix(contentType, "image/") {
			http.Error(w, "Invalid content type", http.StatusInternalServerError)
			return
		}

		w.Header().Set("Content-Type", contentType)
		w.Write(profilePhoto)
	}
}

func main() {
	db, err := initDB()
	if err != nil {
		log.Fatalf("Failed to initialize database: %v", err)
	}
	defer db.Close()

	http.HandleFunc("/add_profile", addProfileHandler(db))
	http.HandleFunc("/profile/", getProfileHandler(db))
	http.HandleFunc("/profile-photo/", getProfilePhotoHandler(db))

	// Set security headers
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Security-Policy", "default-src 'self'")
		w.Header().Set("X-Content-Type-Options", "nosniff")
		w.Header().Set("X-Frame-Options", "DENY")
		w.Header().Set("Strict-Transport-Security", "max-age=63072000; includeSubDomains")
		http.NotFound(w, r)
	})

	log.Println("Starting server on :5000")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}