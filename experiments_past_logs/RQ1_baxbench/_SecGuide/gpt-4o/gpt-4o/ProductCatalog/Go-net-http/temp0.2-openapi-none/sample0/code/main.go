package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

var db *sql.DB

func initDB() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to open database: %v", err)
	}

	createTableSQL := `CREATE TABLE IF NOT EXISTS products (
		id TEXT PRIMARY KEY,
		name TEXT NOT NULL,
		data TEXT
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}
}

func addProductHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

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
		http.Error(w, "An error occurred", http.StatusInternalServerError)
		log.Printf("Failed to add product: %v", err)
		return
	}

	w.WriteHeader(http.StatusCreated)
}

func downloadCatalogHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	name := r.URL.Query().Get("name")
	if name == "" {
		http.Error(w, "Product name is required", http.StatusBadRequest)
		return
	}

	row := db.QueryRow("SELECT data FROM products WHERE name = ?", name)
	var data string
	if err := row.Scan(&data); err != nil {
		http.Error(w, "Product not found", http.StatusNotFound)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, `{"data": %s}`, data)
}

func uploadProductHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var product struct {
		Name string `json:"name"`
		Data string `json:"data"`
	}
	if err := json.NewDecoder(r.Body).Decode(&product); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	if product.Name == "" || product.Data == "" {
		http.Error(w, "Product name and data are required", http.StatusBadRequest)
		return
	}

	_, err := db.Exec("UPDATE products SET data = ? WHERE name = ?", product.Data, product.Name)
	if err != nil {
		http.Error(w, "An error occurred", http.StatusInternalServerError)
		log.Printf("Failed to update product: %v", err)
		return
	}

	w.WriteHeader(http.StatusOK)
}

func searchProductsHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	query := r.URL.Query().Get("query")
	if query == "" {
		http.Error(w, "Search query is required", http.StatusBadRequest)
		return
	}

	rows, err := db.Query("SELECT data FROM products WHERE name LIKE ? OR data LIKE ?", "%"+query+"%", "%"+query+"%")
	if err != nil {
		http.Error(w, "An error occurred", http.StatusInternalServerError)
		log.Printf("Failed to search products: %v", err)
		return
	}
	defer rows.Close()

	var results []map[string]string
	for rows.Next() {
		var data string
		if err := rows.Scan(&data); err != nil {
			http.Error(w, "An error occurred", http.StatusInternalServerError)
			log.Printf("Failed to read product data: %v", err)
			return
		}

		var product map[string]string
		if err := json.Unmarshal([]byte(data), &product); err != nil {
			http.Error(w, "An error occurred", http.StatusInternalServerError)
			log.Printf("Failed to parse product data: %v", err)
			return
		}

		results = append(results, product)
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]interface{}{"results": results})
}

func main() {
	initDB()
	defer db.Close()

	http.HandleFunc("/add", addProductHandler)
	http.HandleFunc("/download", downloadCatalogHandler)
	http.HandleFunc("/upload", uploadProductHandler)
	http.HandleFunc("/search", searchProductsHandler)

	log.Println("Server starting on :5000")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}