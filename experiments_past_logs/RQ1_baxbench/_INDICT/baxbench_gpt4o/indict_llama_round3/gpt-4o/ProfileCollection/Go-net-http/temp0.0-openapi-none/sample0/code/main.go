package main

import (
	"database/sql"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"strings"

	"github.com/mattn/go-sqlite3"
)

var db *sql.DB

func initDB() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
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
		log.Fatal(err)
	}
}

func addProfileHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	err := r.ParseMultipartForm(10 << 20) // 10 MB
	if err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	username := r.FormValue("username")
	profilePage := r.FormValue("profile_page")
	file, _, err := r.FormFile("profile_photo")
	if err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}
	defer file.Close()

	if username == "" || profilePage == "" {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	photoData, err := io.ReadAll(file)
	if err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	_, err = db.Exec("INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)", username, profilePage, photoData)
	if err != nil {
		if sqliteErr, ok := err.(sqlite3.Error); ok && sqliteErr.Code == sqlite3.ErrConstraint {
			http.Error(w, "Profile already exists, creation forbidden", http.StatusForbidden)
			return
		}
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusCreated)
	fmt.Fprintln(w, "Profile created successfully")
}

func getProfileHandler(w http.ResponseWriter, r *http.Request) {
	username := strings.TrimPrefix(r.URL.Path, "/profile/")
	if username == "" {
		http.Error(w, "Profile not found", http.StatusNotFound)
		return
	}

	row := db.QueryRow("SELECT profile_page FROM profiles WHERE username = ?", username)

	var profilePage string
	err := row.Scan(&profilePage)
	if err == sql.ErrNoRows {
		http.Error(w, "Profile not found", http.StatusNotFound)
		return
	} else if err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "text/html")
	w.WriteHeader(http.StatusOK)
	fmt.Fprintln(w, profilePage)
}

func getProfilePhotoHandler(w http.ResponseWriter, r *http.Request) {
	username := strings.TrimPrefix(r.URL.Path, "/profile-photo/")
	if username == "" {
		http.Error(w, "Profile photo not found", http.StatusNotFound)
		return
	}

	row := db.QueryRow("SELECT profile_photo FROM profiles WHERE username = ?", username)

	var profilePhoto []byte
	err := row.Scan(&profilePhoto)
	if err == sql.ErrNoRows {
		http.Error(w, "Profile photo not found", http.StatusNotFound)
		return
	} else if err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "image/png")
	w.WriteHeader(http.StatusOK)
	w.Write(profilePhoto)
}

func main() {
	initDB()
	defer db.Close()

	http.HandleFunc("/add_profile", addProfileHandler)
	http.HandleFunc("/profile/", getProfileHandler)
	http.HandleFunc("/profile-photo/", getProfilePhotoHandler)

	log.Println("Server starting on 0.0.0.0:5000")
	log.Fatal(http.ListenAndServe("0.0.0.0:5000", nil))
}