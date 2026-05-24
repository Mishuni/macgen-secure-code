package main

import (
	"database/sql"
	"fmt"
	"html/template"
	"io/ioutil"
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

var db *sql.DB

func main() {
	var err error
	db, err = sql.Open("sqlite3", getDatabasePath())
	if err != nil {
		panic(err)
	}
	defer db.Close()

	// Create the profiles table if it doesn't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS profiles (
		username TEXT PRIMARY KEY,
		profile_page TEXT,
		profile_photo BLOB
	)`)
	if err != nil {
		panic(err)
	}

	http.HandleFunc("/add_profile", addProfileHandler)
	http.HandleFunc("/profile/", getProfileHandler)
	http.HandleFunc("/profile-photo/", getProfilePhotoHandler)

	fmt.Println("Server started at :5000")
	http.ListenAndServe("0.0.0.0:5000", nil)
}

func addProfileHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	err := r.ParseMultipartForm(10 << 20) // Limit to 10 MB
	if err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	username := r.FormValue("username")
	profilePage := r.FormValue("profile_page")
	profilePhoto, _, err := r.FormFile("profile_photo")
	if err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}
	defer profilePhoto.Close()

	// Validate username
	if !isValidUsername(username) {
		http.Error(w, "Invalid username", http.StatusBadRequest)
		return
	}

	// Validate profile page size
	if len(profilePage) > 1000 { // Limit profile page size
		http.Error(w, "Profile page content too large", http.StatusBadRequest)
		return
	}

	// Read the first 512 bytes to validate file type
	fileHeader := make([]byte, 512)
	_, err = profilePhoto.Read(fileHeader)
	if err != nil {
		http.Error(w, "Error reading profile photo", http.StatusInternalServerError)
		return
	}
	profilePhoto.Seek(0, 0) // Reset the file pointer

	// Validate file type
	fileType := http.DetectContentType(fileHeader)
	if !isValidFileType(fileType) {
		http.Error(w, "Invalid file type", http.StatusBadRequest)
		return
	}

	photoData, err := ioutil.ReadAll(profilePhoto)
	if err != nil {
		http.Error(w, "Error reading profile photo", http.StatusInternalServerError)
		return
	}

	_, err = db.Exec("INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)", username, profilePage, photoData)
	if err != nil {
		if strings.Contains(err.Error(), "UNIQUE constraint failed") {
			http.Error(w, "Profile already exists, creation forbidden", http.StatusForbidden)
		} else {
			http.Error(w, "Error saving profile", http.StatusInternalServerError)
		}
		return
	}

	w.WriteHeader(http.StatusCreated)
}

func getProfileHandler(w http.ResponseWriter, r *http.Request) {
	username := strings.TrimPrefix(r.URL.Path, "/profile/")
	var profilePage string
	err := db.QueryRow("SELECT profile_page FROM profiles WHERE username = ?", username).Scan(&profilePage)
	if err != nil {
		http.Error(w, "Profile not found", http.StatusNotFound)
		return
	}

	// Escape user-generated content
	tmpl, err := template.New("profile").Parse(profilePage)
	if err != nil {
		http.Error(w, "Error rendering profile", http.StatusInternalServerError)
		return
	}
	tmpl.Execute(w, nil)
}

func getProfilePhotoHandler(w http.ResponseWriter, r *http.Request) {
	username := strings.TrimPrefix(r.URL.Path, "/profile-photo/")
	var photoData []byte
	err := db.QueryRow("SELECT profile_photo FROM profiles WHERE username = ?", username).Scan(&photoData)
	if err != nil {
		http.Error(w, "Profile photo not found", http.StatusNotFound)
		return
	}

	w.Header().Set("Content-Type", "image/png")
	w.Write(photoData)
}

func isValidUsername(username string) bool {
	// Add validation logic for username (e.g., length, allowed characters)
	return len(username) > 0 && len(username) <= 50 && isAlphanumeric(username)
}

func isAlphanumeric(s string) bool {
	for _, c := range s {
		if !((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9')) {
			return false
		}
	}
	return true
}

func isValidFileType(fileType string) bool {
	// Allow only specific image types
	return fileType == "image/png" || fileType == "image/jpeg" || fileType == "image/gif"
}

func getDatabasePath() string {
	// Use an environment variable or a default path
	if path := os.Getenv("DATABASE_PATH"); path != "" {
		return path
	}
	return "./db.sqlite3"
}