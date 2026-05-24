package main

import (
	"fmt"
	"mime/multipart"
	"net/http"
	"os"
	"path/filepath"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/mattn/go-sqlite3"
)

type Image struct {
	ID   string `json:"id"`
	Path string `json:"path"`
}

var db *sql.DB

func initDB() {
	var err error
	db, err = sql.Open("sqlite3", "./images.db")
	if err != nil {
		panic(err)
	}

	createTableSQL := `CREATE TABLE IF NOT EXISTS images (
		id TEXT PRIMARY KEY,
		path TEXT NOT NULL
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		panic(err)
	}
}

func uploadImage(c *gin.Context) {
	file, err := c.FormFile("file")
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	// Validate file type
	ext := filepath.Ext(file.Filename)
	if ext != ".jpg" && ext != ".jpeg" && ext != ".png" && ext != ".gif" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Unsupported file type"})
		return
	}

	// Generate a unique ID for the image
	imageID := uuid.New().String()
	filePath := filepath.Join("uploads", imageID+ext)

	// Save the file
	if err := c.SaveUploadedFile(file, filePath); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save image"})
		return
	}

	// Store metadata in the database
	_, err = db.Exec("INSERT INTO images (id, path) VALUES (?, ?)", imageID, filePath)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save image metadata"})
		return
	}

	c.JSON(http.StatusOK, Image{ID: imageID, Path: filePath})
}

func getImage(c *gin.Context) {
	imageID := c.Param("imageId")

	var filePath string
	err := db.QueryRow("SELECT path FROM images WHERE id = ?", imageID).Scan(&filePath)
	if err != nil {
		if err == sql.ErrNoRows {
			c.JSON(http.StatusNotFound, gin.H{"error": "Image not found"})
		} else {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve image"})
		}
		return
	}

	c.File(filePath)
}

func main() {
	initDB()
	defer db.Close()

	r := gin.Default()
	r.POST("/upload", uploadImage)
	r.GET("/images/:imageId", getImage)

	if err := os.MkdirAll("uploads", os.ModePerm); err != nil {
		panic(err)
	}

	r.Run("0.0.0.0:5000")
}