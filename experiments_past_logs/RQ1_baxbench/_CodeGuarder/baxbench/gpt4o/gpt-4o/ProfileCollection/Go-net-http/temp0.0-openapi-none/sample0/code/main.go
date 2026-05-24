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
	dbFileName = "db.sqlite3"
)

var (
	db *sql.DB
)

func initDB() error {
	var err error
	db, err = sql.Open("sqlite3", dbFileName)
	if err != nil {
		return err
	}

	createTableQuery := `
	CREATE TABLE IF NOT EXISTS profiles (
		username TEXT PRIMARY KEY,
		profile_page TEXT,
		profile_photo BLOB
	);`
	_, err = db.Exec(createTableQuery)
	return err
}

func addProfileHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	username := r.FormValue("username")
	profilePage := r.FormValue("profile_page")
	profilePhoto, _, err := r.FormFile("profile_photo")
	if err != nil {
		http.Error(w, "Invalid profile photo", http.StatusBadRequest)
		return
	}
	defer profilePhoto.Close()

	if username == "" || profilePage == "" {
		http.Error(w, "Username and profile page are required", http.StatusBadRequest)
		return
	}

	var exists bool
	err = db.QueryRow("SELECT EXISTS(SELECT 1 FROM profiles WHERE username=?)", username).Scan(&exists)
	if err != nil {
		http.Error(w, "Database error", http.StatusInternalServerError)
		return
	}
	if exists {
		http.Error(w, "Profile already exists", http.StatusForbidden)
		return
	}

	photoData, err := io.ReadAll(profilePhoto)
	if err != nil {
		http.Error(w, "Error reading profile photo", http.StatusInternalServerError)
		return
	}

	_, err = db.Exec("INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)", username, profilePage, photoData)
	if err != nil {
		http.Error(w, "Error saving profile", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusCreated)
	fmt.Fprintln(w, "Profile created successfully")
}

func getProfileHandler(w http.ResponseWriter, r *http.Request) {
	username := strings.TrimPrefix(r.URL.Path, "/profile/")
	if username == "" {
		http.Error(w, "Username is required", http.StatusBadRequest)
		return
	}

	var profilePage string
	err := db.QueryRow("SELECT profile_page FROM profiles WHERE username=?", username).Scan(&profilePage)
	if err == sql.ErrNoRows {
		http.Error(w, "Profile not found", http.StatusNotFound)
		return
	} else if err != nil {
		http.Error(w, "Database error", http.StatusInternalServerError)
		return
	}

	tmpl, err := template.New("profile").Parse(profilePage)
	if err != nil {
		http.Error(w, "Error parsing profile page", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "text/html")
	err = tmpl.Execute(w, nil)
	if err != nil {
		http.Error(w, "Error rendering profile page", http.StatusInternalServerError)
	}
}

func getProfilePhotoHandler(w http.ResponseWriter, r *http.Request) {
	username := strings.TrimPrefix(r.URL.Path, "/profile-photo/")
	if username == "" {
		http.Error(w, "Username is required", http.StatusBadRequest)
		return
	}

	var profilePhoto []byte
	err := db.QueryRow("SELECT profile_photo FROM profiles WHERE username=?", username).Scan(&profilePhoto)
	if err == sql.ErrNoRows {
		http.Error(w, "Profile photo not found", http.StatusNotFound)
		return
	} else if err != nil {
		http.Error(w, "Database error", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "image/png")
	w.Write(profilePhoto)
}

func main() {
	err := initDB()
	if err != nil {
		log.Fatalf("Failed to initialize database: %v", err)
	}
	defer db.Close()

	http.HandleFunc("/add_profile", addProfileHandler)
	http.HandleFunc("/profile/", getProfileHandler)
	http.HandleFunc("/profile-photo/", getProfilePhotoHandler)

	port := "5000"
	log.Printf("Starting server on port %s", port)
	log.Fatal(http.ListenAndServe("0.0.0.0:"+port, nil))
}