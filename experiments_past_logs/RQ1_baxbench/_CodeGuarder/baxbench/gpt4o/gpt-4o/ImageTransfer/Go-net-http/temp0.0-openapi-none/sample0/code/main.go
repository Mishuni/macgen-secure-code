package main

import (
	"database/sql"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

const (
	uploadPath = "./uploads"
	dbPath     = "./images.db"
)

func main() {
	// Initialize the database
	initDB()

	// Create the uploads directory if it doesn't exist
	if _, err := os.Stat(uploadPath); os.IsNotExist(err) {
		os.Mkdir(uploadPath, os.ModePerm)
	}

	http.HandleFunc("/upload", uploadHandler)
	http.HandleFunc("/images/", imageHandler)

	log.Println("Server started on 0.0.0.0:5000")
	log.Fatal(http.ListenAndServe("0.0.0.0:5000", nil))
}

func initDB() {
	db, err := sql.Open("sqlite3", dbPath)
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	createTableSQL := `CREATE TABLE IF NOT EXISTS images (
		"id" TEXT NOT NULL PRIMARY KEY,
		"filename" TEXT,
		"content_type" TEXT
	);`

	_, err = db.Exec(createTableSQL)
	if err != nil {
		log.Fatal(err)
	}
}

func uploadHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	file, header, err := r.FormFile("file")
	if err != nil {
		http.Error(w, "Invalid file", http.StatusBadRequest)
		return
	}
	defer file.Close()

	contentType := header.Header.Get("Content-Type")
	if !isSafeContentType(contentType) {
		http.Error(w, "Unsupported file type", http.StatusBadRequest)
		return
	}

	id := uuid.New().String()
	filename := fmt.Sprintf("%s%s", id, filepath.Ext(header.Filename))
	filePath := filepath.Join(uploadPath, filename)

	out, err := os.Create(filePath)
	if err != nil {
		http.Error(w, "Unable to save the file", http.StatusInternalServerError)
		return
	}
	defer out.Close()

	_, err = io.Copy(out, file)
	if err != nil {
		http.Error(w, "Unable to save the file", http.StatusInternalServerError)
		return
	}

	saveImageMetadata(id, filename, contentType)

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	w.Write([]byte(fmt.Sprintf(`{"id":"%s"}`, id)))
}

func imageHandler(w http.ResponseWriter, r *http.Request) {
	imageID := strings.TrimPrefix(r.URL.Path, "/images/")
	if imageID == "" {
		http.Error(w, "Image ID is required", http.StatusBadRequest)
		return
	}

	filename, contentType, err := getImageMetadata(imageID)
	if err != nil {
		http.Error(w, "Image not found", http.StatusNotFound)
		return
	}

	filePath := filepath.Join(uploadPath, filename)
	http.ServeFile(w, r, filePath)
	w.Header().Set("Content-Type", contentType)
	w.Header().Set("Content-Disposition", "inline")
}

func isSafeContentType(contentType string) bool {
	allowedTypes := []string{"image/jpeg", "image/png", "image/gif"}
	for _, t := range allowedTypes {
		if t == contentType {
			return true
		}
	}
	return false
}

func saveImageMetadata(id, filename, contentType string) {
	db, err := sql.Open("sqlite3", dbPath)
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	insertSQL := `INSERT INTO images (id, filename, content_type) VALUES (?, ?, ?)`
	_, err = db.Exec(insertSQL, id, filename, contentType)
	if err != nil {
		log.Fatal(err)
	}
}

func getImageMetadata(id string) (string, string, error) {
	db, err := sql.Open("sqlite3", dbPath)
	if err != nil {
		return "", "", err
	}
	defer db.Close()

	querySQL := `SELECT filename, content_type FROM images WHERE id = ?`
	row := db.QueryRow(querySQL, id)

	var filename, contentType string
	err = row.Scan(&filename, &contentType)
	if err != nil {
		return "", "", err
	}

	return filename, contentType, nil
}