package main

import (
	"database/sql"
	"fmt"
	"io"
	"log"
	"mime"
	"net/http"
	"os"
	"path/filepath"
	"regexp"

	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

const (
	uploadDir   = "./uploads"
	dbFile      = "./images.db"
	maxFileSize = 10 << 20 // 10 MB
)

var (
	allowedMimeTypes = map[string]bool{
		"image/jpeg": true,
		"image/png":  true,
		"image/gif":  true,
	}
)

func main() {
	// Initialize the database
	initDB()

	// Create upload directory if it doesn't exist
	if _, err := os.Stat(uploadDir); os.IsNotExist(err) {
		err := os.Mkdir(uploadDir, 0700) // Restrict permissions
		if err != nil {
			log.Fatalf("Failed to create upload directory: %v", err)
		}
	}

	http.HandleFunc("/upload", uploadHandler)
	http.HandleFunc("/images/", imageHandler)

	log.Println("Server started at 0.0.0.0:5000")
	log.Fatal(http.ListenAndServe("0.0.0.0:5000", nil))
}

func initDB() {
	db, err := sql.Open("sqlite3", dbFile)
	if err != nil {
		log.Fatalf("Failed to open database: %v", err)
	}
	defer db.Close()

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS images (
		id TEXT PRIMARY KEY,
		filename TEXT NOT NULL
	)`)
	if err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}
}

func uploadHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	r.Body = http.MaxBytesReader(w, r.Body, maxFileSize)
	file, header, err := r.FormFile("file")
	if err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}
	defer func() {
		if err := file.Close(); err != nil {
			log.Printf("Failed to close file: %v", err)
		}
	}()

	// Validate MIME type
	buffer := make([]byte, 512)
	_, err = file.Read(buffer)
	if err != nil {
		http.Error(w, "Invalid file", http.StatusBadRequest)
		return
	}
	file.Seek(0, 0) // Reset file pointer

	mimeType := http.DetectContentType(buffer)
	if !allowedMimeTypes[mimeType] {
		http.Error(w, "Unsupported file type", http.StatusBadRequest)
		return
	}

	// Generate a unique ID for the image
	imageID := uuid.New().String()
	ext, _ := mime.ExtensionsByType(mimeType)
	filename := imageID + ext[0]

	// Save the file
	out, err := os.Create(filepath.Join(uploadDir, filename))
	if err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}
	defer func() {
		if err := out.Close(); err != nil {
			log.Printf("Failed to close output file: %v", err)
		}
	}()

	_, err = io.Copy(out, file)
	if err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}

	// Save the image metadata to the database
	db, err := sql.Open("sqlite3", dbFile)
	if err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}
	defer db.Close()

	_, err = db.Exec("INSERT INTO images (id, filename) VALUES (?, ?)", imageID, filename)
	if err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, `{"id":"%s"}`, imageID)
}

func imageHandler(w http.ResponseWriter, r *http.Request) {
	imageID := filepath.Base(r.URL.Path)
	if !isValidUUID(imageID) {
		http.Error(w, "Invalid image ID", http.StatusBadRequest)
		return
	}

	db, err := sql.Open("sqlite3", dbFile)
	if err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}
	defer db.Close()

	var filename string
	err = db.QueryRow("SELECT filename FROM images WHERE id = ?", imageID).Scan(&filename)
	if err != nil {
		http.Error(w, "Image not found", http.StatusNotFound)
		return
	}

	filePath := filepath.Join(uploadDir, filename)
	file, err := os.Open(filePath)
	if err != nil {
		http.Error(w, "Image not found", http.StatusNotFound)
		return
	}
	defer func() {
		if err := file.Close(); err != nil {
			log.Printf("Failed to close file: %v", err)
		}
	}()

	http.ServeFile(w, r, filePath)
}

func isValidUUID(u string) bool {
	r := regexp.MustCompile(`^[a-fA-F0-9-]{36}$`)
	return r.MatchString(u)
}