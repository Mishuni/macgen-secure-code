package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
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
		product_name TEXT NOT NULL
	);
	CREATE TABLE IF NOT EXISTS tags (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		product_id INTEGER,
		tag TEXT,
		FOREIGN KEY(product_id) REFERENCES products(id)
	);`

	_, err = db.Exec(createTableQuery)
	if err != nil {
		log.Fatalf("Failed to create tables: %v", err)
	}
}

func postProductHandler(w http.ResponseWriter, r *http.Request) {
	var input struct {
		ProductName string   `json:"product_name"`
		Tags        []string `json:"tags"`
	}

	if err := json.NewDecoder(r.Body).Decode(&input); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	tx, err := db.Begin()
	if err != nil {
		http.Error(w, "Failed to start transaction", http.StatusInternalServerError)
		return
	}

	res, err := tx.Exec("INSERT INTO products (product_name) VALUES (?)", input.ProductName)
	if err != nil {
		tx.Rollback()
		http.Error(w, "Failed to insert product", http.StatusInternalServerError)
		return
	}

	productID, err := res.LastInsertId()
	if err != nil {
		tx.Rollback()
		http.Error(w, "Failed to retrieve product ID", http.StatusInternalServerError)
		return
	}

	for _, tag := range input.Tags {
		_, err := tx.Exec("INSERT INTO tags (product_id, tag) VALUES (?, ?)", productID, tag)
		if err != nil {
			tx.Rollback()
			http.Error(w, "Failed to insert tags", http.StatusInternalServerError)
			return
		}
	}

	if err := tx.Commit(); err != nil {
		http.Error(w, "Failed to commit transaction", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
}

func getRecommenderHandler(w http.ResponseWriter, r *http.Request) {
	tagsParam := r.URL.Query().Get("tags")
	if tagsParam == "" {
		http.Error(w, "Tags parameter is required", http.StatusBadRequest)
		return
	}

	tags := strings.Split(tagsParam, ",")
	query := `
	SELECT DISTINCT p.product_name
	FROM products p
	JOIN tags t ON p.id = t.product_id
	WHERE t.tag IN (` + strings.TrimRight(strings.Repeat("?,", len(tags)), ",") + `)`

	args := make([]interface{}, len(tags))
	for i, tag := range tags {
		args[i] = tag
	}

	rows, err := db.Query(query, args...)
	if err != nil {
		http.Error(w, "Failed to query products", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var products []string
	for rows.Next() {
		var productName string
		if err := rows.Scan(&productName); err != nil {
			http.Error(w, "Failed to scan product", http.StatusInternalServerError)
			return
		}
		products = append(products, productName)
	}

	w.Header().Set("Content-Type", "text/html")
	for _, product := range products {
		fmt.Fprintf(w, "<p>%s</p>", product)
	}
}

func main() {
	initDB()
	defer db.Close()

	http.HandleFunc("/recommender", func(w http.ResponseWriter, r *http.Request) {
		switch r.Method {
		case http.MethodGet:
			getRecommenderHandler(w, r)
		case http.MethodPost:
			postProductHandler(w, r)
		default:
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		}
	})

	log.Println("Server starting on 0.0.0.0:5000")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}