package main

import (
	"database/sql"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

const (
	dbFile      = "images.db"
	uploadDir   = "uploads"
	imageBaseURL = "https://localhost:5000/images/"
)

func main() {
	// Create the uploads directory if it doesn't exist
	os.MkdirAll(uploadDir, os.ModePerm)

	// Initialize the database
	initDB()

	http.HandleFunc("/upload", uploadHandler)
	http.HandleFunc("/images/", imageHandler)

	fmt.Println("Server started at http://0.0.0.0:5000")
	http.ListenAndServe("0.0.0.0:5000", nil)
}

func initDB() {
	db, err := sql.Open("sqlite3", dbFile)
	if err != nil {
		logErrorAndRespond(err, nil, http.StatusInternalServerError)
		return
	}
	defer db.Close()

	createTableSQL := `CREATE TABLE IF NOT EXISTS images (
		id TEXT PRIMARY KEY,
		filename TEXT NOT NULL
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		logErrorAndRespond(err, nil, http.StatusInternalServerError)
	}
}

func uploadHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	err := r.ParseMultipartForm(10 << 20) // Limit upload size to 10 MB
	if err != nil {
		http.Error(w, "Unable to parse form", http.StatusBadRequest)
		return
	}

	file, fileHeader, err := r.FormFile("file")
	if err != nil {
		http.Error(w, "File is required", http.StatusBadRequest)
		return
	}
	defer file.Close()

	// Validate file type
	if !isValidImageType(fileHeader) {
		http.Error(w, "Invalid file type", http.StatusBadRequest)
		return
	}

	// Generate a unique ID for the image
	imageID := uuid.New().String()
	filePath := filepath.Join(uploadDir, imageID)

	out, err := os.Create(filePath)
	if err != nil {
		http.Error(w, "Unable to save file", http.StatusInternalServerError)
		return
	}
	defer out.Close()

	// Set file permissions to be more secure
	if err := os.Chmod(filePath, 0600); err != nil {
		http.Error(w, "Unable to set file permissions", http.StatusInternalServerError)
		return
	}

	// Copy the uploaded file to the destination
	if _, err := io.Copy(out, file); err != nil {
		http.Error(w, "Unable to save file", http.StatusInternalServerError)
		return
	}

	// Save the image information in the database
	saveImageInfo(imageID, filepath.Base(filePath))

	// Return the shareable link
	w.Header().Set("Content-Type", "application/json")
	fmt.Fprintf(w, `{"id": "%s"}`, imageID)
}

func isValidImageType(fileHeader *http.FileHeader) bool {
	allowedMIMETypes := []string{"image/jpeg", "image/png", "image/gif"}
	for _, mimeType := range allowedMIMETypes {
		if fileHeader.Header.Get("Content-Type") == mimeType {
			return true
		}
	}
	return false
}

func saveImageInfo(id, filename string) {
	db, err := sql.Open("sqlite3", dbFile)
	if err != nil {
		logErrorAndRespond(err, nil, http.StatusInternalServerError)
		return
	}
	defer db.Close()

	insertSQL := `INSERT INTO images (id, filename) VALUES (?, ?)`
	_, err = db.Exec(insertSQL, id, filename)
	if err != nil {
		logErrorAndRespond(err, nil, http.StatusInternalServerError)
	}
}

func imageHandler(w http.ResponseWriter, r *http.Request) {
	imageID := strings.TrimPrefix(r.URL.Path, "/images/")
	if imageID == "" {
		http.Error(w, "Image ID is required", http.StatusBadRequest)
		return
	}

	db, err := sql.Open("sqlite3", dbFile)
	if err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}
	defer db.Close()

	var filename string
	querySQL := `SELECT filename FROM images WHERE id = ?`
	err = db.QueryRow(querySQL, imageID).Scan(&filename)
	if err != nil {
		if err == sql.ErrNoRows {
			http.Error(w, "Image not found", http.StatusNotFound)
		} else {
			http.Error(w, "Internal server error", http.StatusInternalServerError)
		}
		return
	}

	filePath := filepath.Join(uploadDir, imageID)
	http.ServeFile(w, r, filePath)
}

func logErrorAndRespond(err error, w http.ResponseWriter, statusCode int) {
	if w != nil {
		http.Error(w, "Internal server error", statusCode)
	}
	// Log the error (in a real application, use a logging library)
	fmt.Println("Error:", err)
}