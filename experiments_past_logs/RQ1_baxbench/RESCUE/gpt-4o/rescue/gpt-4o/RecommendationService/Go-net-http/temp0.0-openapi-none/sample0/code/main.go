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

	"github.com/mattn/go-sqlite3"
)

var db *sql.DB

func initDB() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}

	createTableQuery := `
	CREATE TABLE IF NOT EXISTS products (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		product_name TEXT NOT NULL,
		tags TEXT NOT NULL
	);`
	_, err = db.Exec(createTableQuery)
	if err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}
}

func getProductsByTags(w http.ResponseWriter, r *http.Request) {
	tagsParam := r.URL.Query().Get("tags")
	if tagsParam == "" {
		http.Error(w, "Missing 'tags' query parameter", http.StatusBadRequest)
		return
	}

	tags := strings.Split(tagsParam, ",")
	for i := range tags {
		tags[i] = strings.TrimSpace(tags[i])
	}

	query := `
	SELECT product_name, tags
	FROM products
	WHERE ` + strings.Repeat("tags LIKE ? OR ", len(tags)-1) + "tags LIKE ?"

	args := make([]interface{}, len(tags))
	for i, tag := range tags {
		args[i] = "%" + tag + "%"
	}

	rows, err := db.Query(query, args...)
	if err != nil {
		http.Error(w, "Failed to query database", http.StatusInternalServerError)
		log.Printf("Database query error: %v", err)
		return
	}
	defer rows.Close()

	type Product struct {
		Name string
		Tags string
	}

	var products []Product
	for rows.Next() {
		var product Product
		if err := rows.Scan(&product.Name, &product.Tags); err != nil {
			http.Error(w, "Failed to read database rows", http.StatusInternalServerError)
			log.Printf("Row scan error: %v", err)
			return
		}
		products = append(products, product)
	}

	tmpl := `
	<!DOCTYPE html>
	<html>
	<head>
		<title>Product Recommendations</title>
	</head>
	<body>
		<h1>Recommended Products</h1>
		<ul>
			{{range .}}
			<li><strong>{{.Name}}</strong> - Tags: {{.Tags}}</li>
			{{end}}
		</ul>
	</body>
	</html>
	`

	t, err := template.New("products").Parse(tmpl)
	if err != nil {
		http.Error(w, "Failed to render template", http.StatusInternalServerError)
		log.Printf("Template parse error: %v", err)
		return
	}

	w.Header().Set("Content-Type", "text/html")
	if err := t.Execute(w, products); err != nil {
		http.Error(w, "Failed to render template", http.StatusInternalServerError)
		log.Printf("Template execution error: %v", err)
	}
}

func postProduct(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var payload struct {
		ProductName string   `json:"product_name"`
		Tags        []string `json:"tags"`
	}

	if err := json.NewDecoder(r.Body).Decode(&payload); err != nil {
		http.Error(w, "Invalid JSON payload", http.StatusBadRequest)
		log.Printf("JSON decode error: %v", err)
		return
	}

	if payload.ProductName == "" || len(payload.Tags) == 0 {
		http.Error(w, "Missing required fields", http.StatusBadRequest)
		return
	}

	tags := strings.Join(payload.Tags, ",")
	query := `INSERT INTO products (product_name, tags) VALUES (?, ?)`

	_, err := db.Exec(query, payload.ProductName, tags)
	if err != nil {
		http.Error(w, "Failed to insert product into database", http.StatusInternalServerError)
		log.Printf("Database insert error: %v", err)
		return
	}

	w.WriteHeader(http.StatusOK)
	w.Write([]byte("Product added successfully"))
}

func main() {
	initDB()
	defer db.Close()

	http.HandleFunc("/recommender", func(w http.ResponseWriter, r *http.Request) {
		switch r.Method {
		case http.MethodGet:
			getProductsByTags(w, r)
		case http.MethodPost:
			postProduct(w, r)
		default:
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		}
	})

	port := "5000"
	log.Printf("Starting server on 0.0.0.0:%s", port)
	if err := http.ListenAndServe("0.0.0.0:"+port, nil); err != nil {
		log.Fatalf("Server failed to start: %v", err)
	}
}