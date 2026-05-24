package main

import (
	"bytes"
	"database/sql"
	"fmt"
	"mime/multipart"
	"net/http"
	"os"
	"path/filepath"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

var db *sql.DB

type Image struct {
	ID   string
	Path string
}

func initDB() {
	var err error
	db, err = sql.Open("sqlite3", "./images.db")
	if err != nil {
		panic(err)
	}
	createTableSQL := `CREATE TABLE IF NOT EXISTS images (
		id TEXT PRIMARY KEY,
		path TEXT
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
	fileContent, err := file.Open()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Could not open file"})
		return
	}
	defer fileContent.Close()

	buff := make([]byte, 512)
	if _, err := fileContent.Read(buff); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Could not read file"})
		return
	}
	fileContent.Seek(0, 0) // Reset the read pointer

	if !isValidImageType(buff) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid image type"})
		return
	}

	id := uuid.New().String()
	filePath := filepath.Join("uploads", id+filepath.Ext(file.Filename))

	if err := os.MkdirAll("uploads", os.ModePerm|os.ModeDir); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Could not create upload directory"})
		return
	}

	if err := c.SaveUploadedFile(file, filePath); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Could not save file"})
		return
	}

	_, err = db.Exec("INSERT INTO images (id, path) VALUES (?, ?)", id, filePath)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Could not save image metadata"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"id": id})
}

func isValidImageType(buff []byte) bool {
	contentType := http.DetectContentType(buff)
	return contentType == "image/jpeg" || contentType == "image/png" || contentType == "image/gif"
}

func shareImage(c *gin.Context) {
	imageId := c.Param("imageId")
	var image Image

	err := db.QueryRow("SELECT id, path FROM images WHERE id = ?", imageId).Scan(&image.ID, &image.Path)
	if err != nil {
		if err == sql.ErrNoRows {
			c.JSON(http.StatusNotFound, gin.H{"error": "Image not found"})
		} else {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		}
		return
	}

	c.File(image.Path)
}

func main() {
	initDB()
	defer db.Close()

	r := gin.Default()
	r.POST("/upload", uploadImage)
	r.GET("/images/:imageId", shareImage)

	if err := r.Run("0.0.0.0:5000"); err != nil {
		panic(err)
	}
}