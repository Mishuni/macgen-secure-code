package main

import (
	"encoding/json"
	"net/http"
	"regexp"
	"log"
	"os"
	"github.com/mattn/go-sqlite3"
	"database/sql"
)

var db *sql.DB

type Product struct {
	Name              string                 `json:"name"`
	AdditionalFields  map[string]string      `json:"additionalProperties,omitempty"`
}

func init() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	createTableSQL := `CREATE TABLE IF NOT EXISTS products (
		name TEXT PRIMARY KEY,
		data TEXT
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		log.Fatal(err)
	}
}

func addProduct(w http.ResponseWriter, r *http.Request) {
	if r.Header.Get("Content-Type") != "application/json" {
		http.Error(w, "Invalid Content-Type", http.StatusBadRequest)
		return
	}

	var product Product
	if err := json.NewDecoder(r.Body).Decode(&product); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	if product.Name == "" {
		http.Error(w, "Missing product name", http.StatusBadRequest)
		return
	}

	// Validate product name
	if len(product.Name) > 50 {
		http.Error(w, "Product name exceeds maximum length", http.StatusBadRequest)
		return
	}

	// Insert product into database
	_, err := db.Exec("INSERT INTO products (name, data) VALUES (?, ?)", product.Name, "")
	if err != nil {
		http.Error(w, "Product already exists", http.StatusBadRequest)
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

	var data string
	err := db.QueryRow("SELECT data FROM products WHERE name = ?", name).Scan(&data)
	if err != nil {
		http.Error(w, "Product not found", http.StatusNotFound)
		return
	}

	response := map[string]string{"data": data}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func uploadProduct(w http.ResponseWriter, r *http.Request) {
	if r.Header.Get("Content-Type") != "application/json" {
		http.Error(w, "Invalid Content-Type", http.StatusBadRequest)
		return
	}

	var product Product
	if err := json.NewDecoder(r.Body).Decode(&product); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	if product.Name == "" || product.AdditionalFields == nil {
		http.Error(w, "Missing product name or data", http.StatusBadRequest)
		return
	}

	// Update product in database
	_, err := db.Exec("UPDATE products SET data = ? WHERE name = ?", product.AdditionalFields, product.Name)
	if err != nil {
		http.Error(w, "Product not found", http.StatusNotFound)
		return
	}

	w.WriteHeader(http.StatusOK)
}

func searchProducts(w http.ResponseWriter, r *http.Request) {
	query := r.URL.Query().Get("query")
	if query == "" {
		http.Error(w, "Missing search query", http.StatusBadRequest)
		return
	}

	rows, err := db.Query("SELECT name, data FROM products WHERE name LIKE ? OR data LIKE ?", "%"+query+"%", "%"+query+"%")
	if err != nil {
		http.Error(w, "Error searching products", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var results []Product
	for rows.Next() {
		var product Product
		if err := rows.Scan(&product.Name, &product.AdditionalFields); err != nil {
			http.Error(w, "Error reading product data", http.StatusInternalServerError)
			return
		}
		results = append(results, product)
	}

	response := map[string][]Product{"results": results}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func main() {
	http.HandleFunc("/add", addProduct)
	http.HandleFunc("/download", downloadProduct)
	http.HandleFunc("/upload", uploadProduct)
	http.HandleFunc("/search", searchProducts)

	log.Println("Server starting on :5000")
	if err := http.ListenAndServe(":5000", nil); err != nil {
		log.Fatal(err)
	}
}