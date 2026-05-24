package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"strings"

	_ "github.com/mattn/go-sqlite3"
)

var db *sql.DB

func initDB() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to open database: %v", err)
	}

	createTableQuery := `
	CREATE TABLE IF NOT EXISTS products (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		product_name TEXT NOT NULL,
		tags TEXT NOT NULL
	);
	`
	_, err = db.Exec(createTableQuery)
	if err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}
}

func getProductsByTags(w http.ResponseWriter, r *http.Request) {
	tagsParam := r.URL.Query().Get("tags")
	if tagsParam == "" {
		http.Error(w, "Tags parameter is required", http.StatusBadRequest)
		return
	}

	tags := strings.Split(tagsParam, ",")
	for i := range tags {
		tags[i] = strings.TrimSpace(tags[i])
	}

	query := "SELECT product_name, tags FROM products WHERE "
	args := []interface{}{}
	for i, tag := range tags {
		if i > 0 {
			query += " OR "
		}
		query += "tags LIKE ?"
		args = append(args, "%"+tag+"%")
	}

	rows, err := db.Query(query, args...)
	if err != nil {
		http.Error(w, "Failed to query products", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var products []string
	for rows.Next() {
		var productName, productTags string
		if err := rows.Scan(&productName, &productTags); err != nil {
			http.Error(w, "Failed to scan product", http.StatusInternalServerError)
			return
		}
		products = append(products, fmt.Sprintf("<div><h3>%s</h3><p>Tags: %s</p></div>", productName, productTags))
	}

	w.Header().Set("Content-Type", "text/html")
	w.WriteHeader(http.StatusOK)
	for _, product := range products {
		fmt.Fprintln(w, product)
	}
}

func postProduct(w http.ResponseWriter, r *http.Request) {
	var product struct {
		ProductName string   `json:"product_name"`
		Tags        []string `json:"tags"`
	}

	if err := json.NewDecoder(r.Body).Decode(&product); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	if product.ProductName == "" || len(product.Tags) == 0 {
		http.Error(w, "Product name and tags are required", http.StatusBadRequest)
		return
	}

	tags := strings.Join(product.Tags, ",")
	_, err := db.Exec("INSERT INTO products (product_name, tags) VALUES (?, ?)", product.ProductName, tags)
	if err != nil {
		http.Error(w, "Failed to insert product", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
	fmt.Fprintln(w, "Product added successfully")
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
	log.Printf("Starting server on port %s", port)
	if err := http.ListenAndServe("0.0.0.0:"+port, nil); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}