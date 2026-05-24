package main

import (
	"database/sql"
	"encoding/json"
	"log"
	"net/http"
	"os"

	"github.com/mattn/go-sqlite3"
)

var db *sql.DB

func init() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}

	// Create the products table if it doesn't exist
	_, err = db.Exec(`
		CREATE TABLE IF NOT EXISTS products (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			name TEXT NOT NULL UNIQUE,
			data TEXT NOT NULL
		)
	`)
	if err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}
}

func main() {
	http.HandleFunc("/add", addProductHandler)
	http.HandleFunc("/download", downloadProductHandler)
	http.HandleFunc("/upload", uploadProductHandler)
	http.HandleFunc("/search", searchProductHandler)

	log.Println("Server started on 0.0.0.0:5000")
	log.Fatal(http.ListenAndServe("0.0.0.0:5000", nil))
}

func addProductHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid method", http.StatusMethodNotAllowed)
		return
	}

	var product map[string]string
	if err := json.NewDecoder(r.Body).Decode(&product); err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}

	name, ok := product["name"]
	if !ok || name == "" {
		http.Error(w, "Missing or empty 'name' field", http.StatusBadRequest)
		return
	}

	data, err := json.Marshal(product)
	if err != nil {
		http.Error(w, "Failed to process product data", http.StatusInternalServerError)
		return
	}

	_, err = db.Exec("INSERT INTO products (name, data) VALUES (?, ?)", name, string(data))
	if err != nil {
		if sqliteErr, ok := err.(sqlite3.Error); ok && sqliteErr.Code == sqlite3.ErrConstraint {
			http.Error(w, "Product with the same name already exists", http.StatusBadRequest)
		} else {
			http.Error(w, "Failed to add product", http.StatusInternalServerError)
		}
		return
	}

	w.WriteHeader(http.StatusCreated)
}

func downloadProductHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		http.Error(w, "Invalid method", http.StatusMethodNotAllowed)
		return
	}

	name := r.URL.Query().Get("name")
	if name == "" {
		http.Error(w, "Missing 'name' query parameter", http.StatusBadRequest)
		return
	}

	row := db.QueryRow("SELECT data FROM products WHERE name = ?", name)
	var data string
	if err := row.Scan(&data); err != nil {
		if err == sql.ErrNoRows {
			http.Error(w, "Product not found", http.StatusNotFound)
		} else {
			http.Error(w, "Failed to retrieve product", http.StatusInternalServerError)
		}
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{"data": data})
}

func uploadProductHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid method", http.StatusMethodNotAllowed)
		return
	}

	var payload struct {
		Name string `json:"name"`
		Data string `json:"data"`
	}
	if err := json.NewDecoder(r.Body).Decode(&payload); err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}

	if payload.Name == "" || payload.Data == "" {
		http.Error(w, "Missing 'name' or 'data' field", http.StatusBadRequest)
		return
	}

	_, err := db.Exec("UPDATE products SET data = ? WHERE name = ?", payload.Data, payload.Name)
	if err != nil {
		http.Error(w, "Failed to update product", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
}

func searchProductHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		http.Error(w, "Invalid method", http.StatusMethodNotAllowed)
		return
	}

	query := r.URL.Query().Get("query")
	if query == "" {
		http.Error(w, "Missing 'query' parameter", http.StatusBadRequest)
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
			http.Error(w, "Failed to process search results", http.StatusInternalServerError)
			return
		}

		var product map[string]string
		if err := json.Unmarshal([]byte(data), &product); err != nil {
			http.Error(w, "Failed to parse product data", http.StatusInternalServerError)
			return
		}
		results = append(results, product)
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{"results": results})
}