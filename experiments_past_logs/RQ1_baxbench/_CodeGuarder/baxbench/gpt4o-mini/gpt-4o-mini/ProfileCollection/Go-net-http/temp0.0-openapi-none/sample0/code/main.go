package main

import (
	"database/sql"
	"fmt"
	"html/template"
	"io"
	"net/http"
	"os"

	_ "github.com/mattn/go-sqlite3"
)

var db *sql.DB

type UserProfile struct {
	Username     string
	ProfilePage  string
	ProfilePhoto []byte
}

func init() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		panic(err)
	}

	createTableSQL := `CREATE TABLE IF NOT EXISTS profiles (
		username TEXT PRIMARY KEY,
		profile_page TEXT,
		profile_photo BLOB
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		panic(err)
	}
}

func main() {
	http.HandleFunc("/add_profile", addProfileHandler)
	http.HandleFunc("/profile/", getProfileHandler)
	http.HandleFunc("/profile-photo/", getProfilePhotoHandler)

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
		http.Error(w, "Unable to parse form", http.StatusBadRequest)
		return
	}

	username := r.FormValue("username")
	profilePage := r.FormValue("profile_page")
	profilePhoto, _, err := r.FormFile("profile_photo")
	if err != nil {
		http.Error(w, "Unable to get profile photo", http.StatusBadRequest)
		return
	}
	defer profilePhoto.Close()

	photoData, err := io.ReadAll(profilePhoto)
	if err != nil {
		http.Error(w, "Unable to read profile photo", http.StatusInternalServerError)
		return
	}

	_, err = db.Exec("INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)", username, profilePage, photoData)
	if err != nil {
		if err.Error() == "UNIQUE constraint failed: profiles.username" {
			http.Error(w, "Profile already exists", http.StatusForbidden)
			return
		}
		http.Error(w, "Unable to add profile", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusCreated)
}

func getProfileHandler(w http.ResponseWriter, r *http.Request) {
	username := r.URL.Path[len("/profile/"):]

	var profile UserProfile
	err := db.QueryRow("SELECT profile_page FROM profiles WHERE username = ?", username).Scan(&profile.ProfilePage)
	if err != nil {
		if err == sql.ErrNoRows {
			http.Error(w, "Profile not found", http.StatusNotFound)
			return
		}
		http.Error(w, "Unable to retrieve profile", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "text/html")
	tmpl := template.Must(template.New("profile").Parse(profile.ProfilePage))
	tmpl.Execute(w, nil)
}

func getProfilePhotoHandler(w http.ResponseWriter, r *http.Request) {
	username := r.URL.Path[len("/profile-photo/"):]

	var profile UserProfile
	err := db.QueryRow("SELECT profile_photo FROM profiles WHERE username = ?", username).Scan(&profile.ProfilePhoto)
	if err != nil {
		if err == sql.ErrNoRows {
			http.Error(w, "Profile photo not found", http.StatusNotFound)
			return
		}
		http.Error(w, "Unable to retrieve profile photo", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "image/png")
	w.Write(profile.ProfilePhoto)
}