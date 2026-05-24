package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/mattn/go-sqlite3"
	"github.com/google/uuid"
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
		id TEXT PRIMARY KEY,
		name TEXT NOT NULL UNIQUE,
		data TEXT
	);`
	_, err = db.Exec(createTableQuery)
	if err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}
}

func addProduct(w http.ResponseWriter, r *http.Request) {
	var product map[string]string
	if err := json.NewDecoder(r.Body).Decode(&product); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	name, exists := product["name"]
	if !exists || name == "" {
		http.Error(w, "Product name is required", http.StatusBadRequest)
		return
	}

	data, err := json.Marshal(product)
	if err != nil {
		http.Error(w, "Failed to process product data", http.StatusInternalServerError)
		return
	}

	id := uuid.New().String()
	_, err = db.Exec("INSERT INTO products (id, name, data) VALUES (?, ?, ?)", id, name, string(data))
	if err != nil {
		http.Error(w, "Failed to add product", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusCreated)
}

func downloadProduct(w http.ResponseWriter, r *http.Request) {
	name := r.URL.Query().Get("name")
	if name == "" {
		http.Error(w, "Product name is required", http.StatusBadRequest)
		return
	}

	var data string
	err := db.QueryRow("SELECT data FROM products WHERE name = ?", name).Scan(&data)
	if err != nil {
		http.Error(w, "Product not found", http.StatusNotFound)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.Write([]byte(data))
}

func uploadProduct(w http.ResponseWriter, r *http.Request) {
	var product map[string]string
	if err := json.NewDecoder(r.Body).Decode(&product); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	name, exists := product["name"]
	if !exists || name == "" {
		http.Error(w, "Product name is required", http.StatusBadRequest)
		return
	}

	data, exists := product["data"]
	if !exists {
		http.Error(w, "Product data is required", http.StatusBadRequest)
		return
	}

	_, err := db.Exec("UPDATE products SET data = ? WHERE name = ?", data, name)
	if err != nil {
		http.Error(w, "Failed to update product", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
}

func searchProducts(w http.ResponseWriter, r *http.Request) {
	query := r.URL.Query().Get("query")
	if query == "" {
		http.Error(w, "Search query is required", http.StatusBadRequest)
		return
	}

	rows, err := db.Query("SELECT data FROM products WHERE name LIKE ? OR data LIKE ?", "%"+query+"%", "%"+query+"%")
	if err != nil {
		http.Error(w, "Failed to search products", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var results []map[string]string
	for rows.Next() {
		var data string
		if err := rows.Scan(&data); err != nil {
			http.Error(w, "Failed to read product data", http.StatusInternalServerError)
			return
		}

		var product map[string]string
		if err := json.Unmarshal([]byte(data), &product); err != nil {
			http.Error(w, "Failed to parse product data", http.StatusInternalServerError)
			return
		}

		results = append(results, product)
	}

	response := map[string]interface{}{
		"results": results,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func main() {
	initDB()
	defer db.Close()

	http.HandleFunc("/add", addProduct)
	http.HandleFunc("/download", downloadProduct)
	http.HandleFunc("/upload", uploadProduct)
	http.HandleFunc("/search", searchProducts)

	port := "5000"
	fmt.Printf("Server is running on port %s\n", port)
	log.Fatal(http.ListenAndServe("0.0.0.0:"+port, nil))
}