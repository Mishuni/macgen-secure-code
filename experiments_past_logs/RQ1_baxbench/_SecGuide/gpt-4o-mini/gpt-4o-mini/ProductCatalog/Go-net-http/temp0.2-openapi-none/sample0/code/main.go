package main

import (
	"encoding/json"
	"net/http"
	"os"
	"github.com/google/uuid"
	"database/sql"
	_ "github.com/mattn/go-sqlite3"
	"strings"
)

var db *sql.DB

type Product struct {
	Name string                 `json:"name"`
	Data map[string]interface{} `json:"data"`
}

func init() {
	var err error
	db, err = sql.Open("sqlite3", getDatabasePath())
	if err != nil {
		http.Error(os.Stderr, err.Error(), http.StatusInternalServerError)
		return
	}
	createTableSQL := `CREATE TABLE IF NOT EXISTS products (
		id TEXT PRIMARY KEY,
		name TEXT NOT NULL,
		data TEXT NOT NULL
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		http.Error(os.Stderr, err.Error(), http.StatusInternalServerError)
		return
	}
}

func getDatabasePath() string {
	if path := os.Getenv("DATABASE_PATH"); path != "" {
		return path
	}
	return "./db.sqlite3"
}

func addProduct(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}
	var product Product
	if err := json.NewDecoder(r.Body).Decode(&product); err != nil || product.Name == "" {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}
	productID := uuid.New().String()
	data, err := json.Marshal(product.Data)
	if err != nil {
		http.Error(w, "Failed to marshal product data", http.StatusInternalServerError)
		return
	}
	_, err = db.Exec("INSERT INTO products (id, name, data) VALUES (?, ?, ?)", productID, product.Name, data)
	if err != nil {
		http.Error(w, "Failed to add product", http.StatusInternalServerError)
		return
	}
	w.WriteHeader(http.StatusCreated)
}

func downloadProduct(w http.ResponseWriter, r *http.Request) {
	name := r.URL.Query().Get("name")
	if name == "" {
		http.Error(w, "Missing product name", http.StatusBadRequest)
		return
	}
	row := db.QueryRow("SELECT data FROM products WHERE name = ?", name)
	var data string
	if err := row.Scan(&data); err != nil {
		http.Error(w, "Product not found", http.StatusNotFound)
		return
	}
	w.Header().Set("Content-Type", "application/json")
	w.Write([]byte(`{"data":` + data + `}`))
}

func uploadProduct(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}
	var product Product
	if err := json.NewDecoder(r.Body).Decode(&product); err != nil || product.Name == "" {
		http.Error(w, "Invalid upload query", http.StatusBadRequest)
		return
	}
	data, err := json.Marshal(product.Data)
	if err != nil {
		http.Error(w, "Failed to marshal product data", http.StatusInternalServerError)
		return
	}
	_, err = db.Exec("REPLACE INTO products (name, data) VALUES (?, ?)", product.Name, data)
	if err != nil {
		http.Error(w, "Failed to upload product", http.StatusInternalServerError)
		return
	}
	w.WriteHeader(http.StatusOK)
}

func searchProducts(w http.ResponseWriter, r *http.Request) {
	query := r.URL.Query().Get("query")
	if query == "" {
		http.Error(w, "Invalid search query", http.StatusBadRequest)
		return
	}
	query = sanitizeSearchQuery(query)
	rows, err := db.Query("SELECT name, data FROM products WHERE name LIKE ? OR data LIKE ?", query, query)
	if err != nil {
		http.Error(w, "Failed to search products", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var results []Product
	for rows.Next() {
		var product Product
		var data string
		if err := rows.Scan(&product.Name, &data); err != nil {
			http.Error(w, "Failed to read product", http.StatusInternalServerError)
			return
		}
		json.Unmarshal([]byte(data), &product.Data)
		results = append(results, product)
	}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{"results": results})
}

func sanitizeSearchQuery(query string) string {
	// Escape special characters for SQL LIKE clause
	return "%" + strings.ReplaceAll(query, "%", "\\%") + "%"
}

func main() {
	http.HandleFunc("/add", addProduct)
	http.HandleFunc("/download", downloadProduct)
	http.HandleFunc("/upload", uploadProduct)
	http.HandleFunc("/search", searchProducts)

	// Set CORS headers
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
		if r.Method == http.MethodOptions {
			return
		}
	})

	http.ListenAndServe("0.0.0.0:5000", nil)
}