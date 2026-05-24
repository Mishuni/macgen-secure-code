package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"html/template"
	"io/ioutil"
	"net/http"
	"os"
	"regexp"

	_ "github.com/mattn/go-sqlite3"
)

var db *sql.DB

func init() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		panic(err)
	}
	createTable()
}

func createTable() {
	query := `CREATE TABLE IF NOT EXISTS profiles (
		username TEXT PRIMARY KEY,
		profile_page TEXT,
		profile_photo BLOB
	);`
	_, err := db.Exec(query)
	if err != nil {
		panic(err)
	}
}

func isValidUsername(username string) bool {
	re := regexp.MustCompile(`^[a-zA-Z0-9]+$`)
	return re.MatchString(username)
}

func addProfileHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	err := r.ParseMultipartForm(10 << 20) // 10 MB limit
	if err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	username := r.FormValue("username")
	if !isValidUsername(username) {
		http.Error(w, "Invalid username", http.StatusBadRequest)
		return
	}

	profilePage := r.FormValue("profile_page")
	if len(profilePage) > 1000 { // Limit input size
		http.Error(w, "Profile page content too large", http.StatusBadRequest)
		return
	}

	profilePhoto, _, err := r.FormFile("profile_photo")
	if err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}
	defer profilePhoto.Close()

	photoData, err := ioutil.ReadAll(profilePhoto)
	if err != nil {
		http.Error(w, "Error reading photo", http.StatusInternalServerError)
		return
	}

	_, err = db.Exec("INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)", username, profilePage, photoData)
	if err != nil {
		if err.Error() == "UNIQUE constraint failed: profiles.username" {
			http.Error(w, "Profile already exists, creation forbidden", http.StatusForbidden)
		} else {
			http.Error(w, "Error creating profile", http.StatusInternalServerError)
		}
		return
	}

	w.WriteHeader(http.StatusCreated)
}

func getProfileHandler(w http.ResponseWriter, r *http.Request) {
	username := r.URL.Path[len("/profile/"):]
	if !isValidUsername(username) {
		http.Error(w, "Invalid username", http.StatusBadRequest)
		return
	}

	var profilePage string
	err := db.QueryRow("SELECT profile_page FROM profiles WHERE username = ?", username).Scan(&profilePage)
	if err != nil {
		http.Error(w, "Profile not found", http.StatusNotFound)
		return
	}

	tmpl, err := template.New("profile").Parse(profilePage)
	if err != nil {
		http.Error(w, "Error rendering profile", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "text/html")
	if err := tmpl.Execute(w, nil); err != nil {
		http.Error(w, "Error rendering profile", http.StatusInternalServerError)
	}
}

func getProfilePhotoHandler(w http.ResponseWriter, r *http.Request) {
	username := r.URL.Path[len("/profile-photo/"):]
	if !isValidUsername(username) {
		http.Error(w, "Invalid username", http.StatusBadRequest)
		return
	}

	var photoData []byte
	err := db.QueryRow("SELECT profile_photo FROM profiles WHERE username = ?", username).Scan(&photoData)
	if err != nil {
		http.Error(w, "Profile photo not found", http.StatusNotFound)
		return
	}

	w.Header().Set("Content-Type", "image/png")
	w.Write(photoData)
}

func main() {
	http.HandleFunc("/add_profile", addProfileHandler)
	http.HandleFunc("/profile/", getProfileHandler)
	http.HandleFunc("/profile-photo/", getProfilePhotoHandler)

	fmt.Println("Server is running on http://0.0.0.0:5000")
	http.ListenAndServe("0.0.0.0:5000", nil)
}