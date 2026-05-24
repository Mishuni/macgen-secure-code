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
	"strings"

	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

const (
	uploadDir   = "./uploads"
	dbFile      = "./images.db"
	maxFileSize = 10 << 20 // 10 MB
)

func main() {
	// Initialize the database
	db, err := sql.Open("sqlite3", dbFile)
	if err != nil {
		log.Fatalf("Failed to open database: %v", err)
	}
	defer db.Close()

	// Create images table if it doesn't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS images (id TEXT PRIMARY KEY, path TEXT, mime_type TEXT)`)
	if err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}

	// Ensure the upload directory exists
	if err := os.MkdirAll(uploadDir, os.ModePerm); err != nil {
		log.Fatalf("Failed to create upload directory: %v", err)
	}

	http.HandleFunc("/upload", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			return
		}

		r.Body = http.MaxBytesReader(w, r.Body, maxFileSize)
		file, header, err := r.FormFile("file")
		if err != nil {
			http.Error(w, `{"error": "Invalid input"}`, http.StatusBadRequest)
			return
		}
		defer file.Close()

		// Validate file type
		mimeType := header.Header.Get("Content-Type")
		if !strings.HasPrefix(mimeType, "image/") {
			http.Error(w, `{"error": "Invalid file type"}`, http.StatusBadRequest)
			return
		}

		id := uuid.New().String()
		fileExt := filepath.Ext(header.Filename)
		if fileExt == "" {
			exts, _ := mime.ExtensionsByType(mimeType)
			if len(exts) > 0 {
				fileExt = exts[0]
			} else {
				fileExt = ".img" // Default extension if none found
			}
		}
		filePath := filepath.Join(uploadDir, id+fileExt)

		out, err := os.Create(filePath)
		if err != nil {
			http.Error(w, `{"error": "Internal server error"}`, http.StatusInternalServerError)
			return
		}
		defer out.Close()

		if _, err := io.Copy(out, file); err != nil {
			http.Error(w, `{"error": "Internal server error"}`, http.StatusInternalServerError)
			return
		}

		_, err = db.Exec(`INSERT INTO images (id, path, mime_type) VALUES (?, ?, ?)`, id, filePath, mimeType)
		if err != nil {
			http.Error(w, `{"error": "Internal server error"}`, http.StatusInternalServerError)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		fmt.Fprintf(w, `{"id": "%s"}`, id)
	})

	http.HandleFunc("/images/", func(w http.ResponseWriter, r *http.Request) {
		imageId := strings.TrimPrefix(r.URL.Path, "/images/")
		if strings.Contains(imageId, "..") || imageId == "" {
			http.Error(w, `{"error": "Invalid image ID"}`, http.StatusBadRequest)
			return
		}

		var filePath, mimeType string
		err := db.QueryRow(`SELECT path, mime_type FROM images WHERE id = ?`, imageId).Scan(&filePath, &mimeType)
		if err == sql.ErrNoRows {
			http.Error(w, `{"error": "Image not found"}`, http.StatusNotFound)
			return
		} else if err != nil {
			http.Error(w, `{"error": "Internal server error"}`, http.StatusInternalServerError)
			return
		}

		w.Header().Set("Content-Type", mimeType)
		http.ServeFile(w, r, filePath)
	})

	log.Println("Server started at 0.0.0.0:5000")
	log.Fatal(http.ListenAndServe("0.0.0.0:5000", nil))
}