package main

import (
	"database/sql"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"regexp"

	"github.com/mattn/go-sqlite3"
)

func isValidUsername(username string) bool {
	validUsername := regexp.MustCompile(`^[a-zA-Z0-9]{1,20}$`)
	return validUsername.MatchString(username)
}

func isValidPNG(file io.Reader) bool {
	buffer := make([]byte, 512)
	_, err := file.Read(buffer)
	if err != nil {
		return false
	}
	contentType := http.DetectContentType(buffer)
	return contentType == "image/png"
}

func main() {
	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS profiles (
		username TEXT PRIMARY KEY,
		profile_page TEXT,
		profile_photo BLOB
	)`)
	if err != nil {
		log.Fatal(err)
	}

	http.HandleFunc("/add_profile", func(w http.ResponseWriter, r *http.Request) {
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

		if !isValidUsername(username) {
			http.Error(w, "Invalid username", http.StatusBadRequest)
			return
		}

		if !isValidPNG(file) {
			http.Error(w, "Invalid file type", http.StatusBadRequest)
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

		photoData, err := io.ReadAll(file)
		if err != nil {
			http.Error(w, "Invalid input", http.StatusBadRequest)
			return
		}

		_, err = db.Exec("INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)", username, profilePage, photoData)
		if err != nil {
			http.Error(w, "Database error", http.StatusInternalServerError)
			return
		}

		w.WriteHeader(http.StatusCreated)
		fmt.Fprintln(w, "Profile created successfully")
	})

	http.HandleFunc("/profile/", func(w http.ResponseWriter, r *http.Request) {
		username := r.URL.Path[len("/profile/"):]
		var profilePage string
		err := db.QueryRow("SELECT profile_page FROM profiles WHERE username=?", username).Scan(&profilePage)
		if err == sql.ErrNoRows {
			http.Error(w, "Profile not found", http.StatusNotFound)
			return
		} else if err != nil {
			http.Error(w, "Database error", http.StatusInternalServerError)
			return
		}

		w.Header().Set("Content-Type", "text/html")
		w.WriteHeader(http.StatusOK)
		fmt.Fprintln(w, profilePage)
	})

	http.HandleFunc("/profile-photo/", func(w http.ResponseWriter, r *http.Request) {
		username := r.URL.Path[len("/profile-photo/"):]
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
		w.WriteHeader(http.StatusOK)
		w.Write(profilePhoto)
	})

	log.Fatal(http.ListenAndServe("0.0.0.0:5000", nil))
}