package main

import (
	"database/sql"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"path/filepath"

	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

const (
	uploadDir = "./uploads"
	dbFile    = "./images.db"
)

func main() {
	// Ensure upload directory exists
	if err := os.MkdirAll(uploadDir, 0755); err != nil {
		log.Fatalf("Failed to create upload directory: %v", err)
	}

	// Initialize database
	db, err := sql.Open("sqlite3", dbFile)
	if err != nil {
		log.Fatalf("Failed to open database: %v", err)
	}
	defer db.Close()

	if err := initializeDatabase(db); err != nil {
		log.Fatalf("Failed to initialize database: %v", err)
	}

	// Set up routes
	http.HandleFunc("/upload", func(w http.ResponseWriter, r *http.Request) {
		handleUpload(w, r, db)
	})
	http.HandleFunc("/images/", func(w http.ResponseWriter, r *http.Request) {
		handleImageView(w, r, db)
	})

	// Start server
	log.Println("Server started on 0.0.0.0:5000")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		log.Fatalf("Server failed: %v", err)
	}
}

func initializeDatabase(db *sql.DB) error {
	query := `
	CREATE TABLE IF NOT EXISTS images (
		id TEXT PRIMARY KEY,
		filename TEXT NOT NULL
	)`
	_, err := db.Exec(query)
	return err
}

func handleUpload(w http.ResponseWriter, r *http.Request, db *sql.DB) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// Parse multipart form
	if err := r.ParseMultipartForm(10 << 20); err != nil {
		http.Error(w, "Failed to parse form", http.StatusBadRequest)
		return
	}

	// Retrieve file
	file, header, err := r.FormFile("file")
	if err != nil {
		http.Error(w, "File is required", http.StatusBadRequest)
		return
	}
	defer file.Close()

	// Validate file name
	if header.Filename == "" || containsInvalidPathChars(header.Filename) {
		http.Error(w, "Invalid file name", http.StatusBadRequest)
		return
	}

	// Generate unique ID and save file
	id := uuid.New().String()
	safeFilename := filepath.Base(header.Filename)
	filePath := filepath.Join(uploadDir, id+"_"+safeFilename)

	out, err := os.Create(filePath)
	if err != nil {
		http.Error(w, "Failed to save file", http.StatusInternalServerError)
		return
	}
	defer out.Close()

	if _, err := io.Copy(out, file); err != nil {
		http.Error(w, "Failed to save file", http.StatusInternalServerError)
		return
	}

	// Store metadata in database
	query := `INSERT INTO images (id, filename) VALUES (?, ?)`
	if _, err := db.Exec(query, id, safeFilename); err != nil {
		http.Error(w, "Failed to save metadata", http.StatusInternalServerError)
		return
	}

	// Respond with shareable link
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, `{"id": "%s"}`, id)
}

func handleImageView(w http.ResponseWriter, r *http.Request, db *sql.DB) {
	if r.Method != http.MethodGet {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// Extract image ID from URL
	imageID := filepath.Base(r.URL.Path[len("/images/"):])
	if imageID == "" || containsInvalidPathChars(imageID) {
		http.Error(w, "Invalid image ID", http.StatusBadRequest)
		return
	}

	// Retrieve file name from database
	var filename string
	query := `SELECT filename FROM images WHERE id = ?`
	if err := db.QueryRow(query, imageID).Scan(&filename); err != nil {
		if err == sql.ErrNoRows {
			http.Error(w, "Image not found", http.StatusNotFound)
		} else {
			http.Error(w, "Failed to retrieve image", http.StatusInternalServerError)
		}
		return
	}

	// Serve the file
	filePath := filepath.Join(uploadDir, imageID+"_"+filename)
	http.ServeFile(w, r, filePath)
}

func containsInvalidPathChars(input string) bool {
	invalidChars := []string{"/", "\\", "\x00"}
	for _, char := range invalidChars {
		if contains(input, char) {
			return true
		}
	}
	return false
}

func contains(input, substr string) bool {
	return len(input) > 0 && len(substr) > 0 && filepath.Clean(input) != input
}