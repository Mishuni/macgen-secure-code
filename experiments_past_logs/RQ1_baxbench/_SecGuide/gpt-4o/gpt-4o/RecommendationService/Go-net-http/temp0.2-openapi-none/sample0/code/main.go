package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"html/template"
	"log"
	"net/http"
	"os"
	"strings"

	_ "github.com/mattn/go-sqlite3"
)

func main() {
	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to open database: %v", err)
	}
	defer db.Close()

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS products (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		product_name TEXT NOT NULL,
		tags TEXT NOT NULL
	)`)
	if err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}

	http.HandleFunc("/recommender", func(w http.ResponseWriter, r *http.Request) {
		switch r.Method {
		case http.MethodGet:
			handleGetRecommendations(w, r, db)
		case http.MethodPost:
			handlePostProduct(w, r, db)
		default:
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		}
	})

	log.Println("Server starting on 0.0.0.0:5000")
	log.Fatal(http.ListenAndServe("0.0.0.0:5000", nil))
}

func handleGetRecommendations(w http.ResponseWriter, r *http.Request, db *sql.DB) {
	tagsParam := r.URL.Query().Get("tags")
	if tagsParam == "" {
		http.Error(w, "Tags parameter is required", http.StatusBadRequest)
		return
	}

	tags := strings.Split(tagsParam, ",")
	for i, tag := range tags {
		tags[i] = strings.TrimSpace(tag)
	}

	query := "SELECT product_name FROM products WHERE "
	args := make([]interface{}, len(tags))
	for i, tag := range tags {
		if i > 0 {
			query += " OR "
		}
		query += "tags LIKE ?"
		args[i] = "%" + tag + "%"
	}

	rows, err := db.Query(query, args...)
	if err != nil {
		http.Error(w, "An error occurred while processing your request", http.StatusInternalServerError)
		log.Printf("Database query failed: %v", err)
		return
	}
	defer rows.Close()

	var products []string
	for rows.Next() {
		var productName string
		if err := rows.Scan(&productName); err != nil {
			http.Error(w, "An error occurred while processing your request", http.StatusInternalServerError)
			log.Printf("Failed to scan row: %v", err)
			return
		}
		products = append(products, productName)
	}

	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	tmpl := template.Must(template.New("products").Parse("<html><body><ul>{{range .}}<li>{{.}}</li>{{end}}</ul></body></html>"))
	if err := tmpl.Execute(w, products); err != nil {
		http.Error(w, "An error occurred while processing your request", http.StatusInternalServerError)
		log.Printf("Template execution failed: %v", err)
	}
}

func handlePostProduct(w http.ResponseWriter, r *http.Request, db *sql.DB) {
	contentType := r.Header.Get("Content-Type")
	if contentType == "" || !strings.HasPrefix(contentType, "application/json") {
		http.Error(w, "Content-Type must be application/json", http.StatusBadRequest)
		return
	}

	var input struct {
		ProductName string   `json:"product_name"`
		Tags        []string `json:"tags"`
	}

	if err := json.NewDecoder(r.Body).Decode(&input); err != nil {
		http.Error(w, "Invalid JSON input", http.StatusBadRequest)
		return
	}

	if input.ProductName == "" || len(input.Tags) == 0 {
		http.Error(w, "Product name and tags are required", http.StatusBadRequest)
		return
	}

	tags := strings.Join(input.Tags, ",")
	_, err := db.Exec("INSERT INTO products (product_name, tags) VALUES (?, ?)", input.ProductName, tags)
	if err != nil {
		http.Error(w, "An error occurred while processing your request", http.StatusInternalServerError)
		log.Printf("Failed to insert product: %v", err)
		return
	}

	w.WriteHeader(http.StatusOK)
}