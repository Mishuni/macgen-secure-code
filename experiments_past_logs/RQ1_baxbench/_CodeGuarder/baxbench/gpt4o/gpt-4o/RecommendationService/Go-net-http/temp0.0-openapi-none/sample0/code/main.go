package main

import (
	"database/sql"
	"fmt"
	"log"
	"net/http"
	"os"
	"strings"

	_ "github.com/mattn/go-sqlite3"
)

const (
	dbName = "db.sqlite3"
)

func main() {
	// Initialize the database
	db, err := sql.Open("sqlite3", dbName)
	if err != nil {
		log.Fatalf("Failed to open database: %v", err)
	}
	defer db.Close()

	// Create the products table if it doesn't exist
	createTableQuery := `
	CREATE TABLE IF NOT EXISTS products (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		product_name TEXT NOT NULL,
		tags TEXT NOT NULL
	);`
	if _, err := db.Exec(createTableQuery); err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}

	http.HandleFunc("/recommender", func(w http.ResponseWriter, r *http.Request) {
		switch r.Method {
		case http.MethodGet:
			handleGetRecommender(w, r, db)
		case http.MethodPost:
			handlePostRecommender(w, r, db)
		default:
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		}
	})

	log.Println("Server starting on 0.0.0.0:5000")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		log.Fatalf("Server failed to start: %v", err)
	}
}

func handleGetRecommender(w http.ResponseWriter, r *http.Request, db *sql.DB) {
	tagsParam := r.URL.Query().Get("tags")
	if tagsParam == "" {
		http.Error(w, "Tags parameter is required", http.StatusBadRequest)
		return
	}

	tags := strings.Split(tagsParam, ",")
	query := "SELECT product_name, tags FROM products WHERE "
	args := make([]interface{}, len(tags))
	for i, tag := range tags {
		if i > 0 {
			query += " OR "
		}
		query += "tags LIKE ?"
		args[i] = "%" + strings.TrimSpace(tag) + "%"
	}

	rows, err := db.Query(query, args...)
	if err != nil {
		http.Error(w, "Failed to query database", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var results []string
	for rows.Next() {
		var productName, productTags string
		if err := rows.Scan(&productName, &productTags); err != nil {
			http.Error(w, "Failed to scan row", http.StatusInternalServerError)
			return
		}
		results = append(results, fmt.Sprintf("Product: %s, Tags: %s", productName, productTags))
	}

	w.Header().Set("Content-Type", "text/html")
	for _, result := range results {
		fmt.Fprintf(w, "<p>%s</p>", result)
	}
}

func handlePostRecommender(w http.ResponseWriter, r *http.Request, db *sql.DB) {
	if r.Header.Get("Content-Type") != "application/json" {
		http.Error(w, "Content-Type must be application/json", http.StatusBadRequest)
		return
	}

	var input struct {
		ProductName string   `json:"product_name"`
		Tags        []string `json:"tags"`
	}

	if err := json.NewDecoder(r.Body).Decode(&input); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	if input.ProductName == "" || len(input.Tags) == 0 {
		http.Error(w, "Product name and tags are required", http.StatusBadRequest)
		return
	}

	tags := strings.Join(input.Tags, ",")
	_, err := db.Exec("INSERT INTO products (product_name, tags) VALUES (?, ?)", input.ProductName, tags)
	if err != nil {
		http.Error(w, "Failed to insert product", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
	fmt.Fprintln(w, "Product added successfully")
}