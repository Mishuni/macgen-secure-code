package main

import (
	"database/sql"
	"fmt"
	"html/template"
	"io/ioutil"
	"net/http"
	"os"

	_ "github.com/mattn/go-sqlite3"
)

var db *sql.DB

func init() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		panic(err)
	}

	// Create the profiles table if it doesn't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS profiles (
		username TEXT PRIMARY KEY,
		profile_page TEXT,
		profile_photo BLOB
	)`)
	if err != nil {
		panic(err)
	}
}

func main() {
	http.HandleFunc("/add_profile", addProfileHandler)
	http.HandleFunc("/profile/", profileHandler)
	http.HandleFunc("/profile-photo/", profilePhotoHandler)

	fmt.Println("Server is running on http://0.0.0.0:5000")
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

	photoData, err := ioutil.ReadAll(profilePhoto)
	if err != nil {
		http.Error(w, "Error reading profile photo", http.StatusInternalServerError)
		return
	}

	// Check if the profile already exists
	var exists bool
	err = db.QueryRow("SELECT EXISTS(SELECT 1 FROM profiles WHERE username = ?)", username).Scan(&exists)
	if err != nil {
		http.Error(w, "Database error", http.StatusInternalServerError)
		return
	}
	if exists {
		http.Error(w, "Profile already exists, creation forbidden", http.StatusForbidden)
		return
	}

	// Insert the new profile
	_, err = db.Exec("INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)", username, profilePage, photoData)
	if err != nil {
		http.Error(w, "Database error", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusCreated)
}

func profileHandler(w http.ResponseWriter, r *http.Request) {
	username := r.URL.Path[len("/profile/"):]

	var profilePage string
	err := db.QueryRow("SELECT profile_page FROM profiles WHERE username = ?", username).Scan(&profilePage)
	if err != nil {
		if err == sql.ErrNoRows {
			http.Error(w, "Profile not found", http.StatusNotFound)
		} else {
			http.Error(w, "Database error", http.StatusInternalServerError)
		}
		return
	}

	w.Header().Set("Content-Type", "text/html")
	w.Write([]byte(profilePage))
}

func profilePhotoHandler(w http.ResponseWriter, r *http.Request) {
	username := r.URL.Path[len("/profile-photo/"):]

	var photoData []byte
	err := db.QueryRow("SELECT profile_photo FROM profiles WHERE username = ?", username).Scan(&photoData)
	if err != nil {
		if err == sql.ErrNoRows {
			http.Error(w, "Profile photo not found", http.StatusNotFound)
		} else {
			http.Error(w, "Database error", http.StatusInternalServerError)
		}
		return
	}

	w.Header().Set("Content-Type", "image/png")
	w.Write(photoData)
}