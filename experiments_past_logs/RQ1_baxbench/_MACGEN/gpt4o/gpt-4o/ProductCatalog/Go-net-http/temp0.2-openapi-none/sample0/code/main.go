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
		properties TEXT
	);`

	_, err = db.Exec(createTableSQL)
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
	if !exists {
		http.Error(w, "Product name is required", http.StatusBadRequest)
		return
	}

	properties, err := json.Marshal(product)
	if err != nil {
		http.Error(w, "Failed to process properties", http.StatusInternalServerError)
		return
	}

	id := uuid.New().String()
	_, err = db.Exec("INSERT INTO products (id, name, properties) VALUES (?, ?, ?)", id, name, string(properties))
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

	row := db.QueryRow("SELECT properties FROM products WHERE name = ?", name)
	var properties string
	if err := row.Scan(&properties); err != nil {
		http.Error(w, "Product not found", http.StatusNotFound)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	w.Write([]byte(fmt.Sprintf(`{"data": %s}`, properties)))
}

func uploadProduct(w http.ResponseWriter, r *http.Request) {
	var payload struct {
		Name string `json:"name"`
		Data string `json:"data"`
	}

	if err := json.NewDecoder(r.Body).Decode(&payload); err != nil {
		http.Error(w, "Invalid upload query", http.StatusBadRequest)
		return
	}

	_, err := db.Exec("UPDATE products SET properties = ? WHERE name = ?", payload.Data, payload.Name)
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

	rows, err := db.Query("SELECT properties FROM products WHERE name LIKE ? OR properties LIKE ?", "%"+query+"%", "%"+query+"%")
	if err != nil {
		http.Error(w, "Failed to search products", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var results []map[string]string
	for rows.Next() {
		var properties string
		if err := rows.Scan(&properties); err != nil {
			http.Error(w, "Failed to read product data", http.StatusInternalServerError)
			return
		}

		var product map[string]string
		if err := json.Unmarshal([]byte(properties), &product); err != nil {
			http.Error(w, "Failed to parse product data", http.StatusInternalServerError)
			return
		}

		results = append(results, product)
	}

	response := map[string]interface{}{
		"results": results,
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
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
	if envPort := os.Getenv("PORT"); envPort != "" {
		port = envPort
	}

	log.Printf("Server starting on port %s", port)
	log.Fatal(http.ListenAndServe("0.0.0.0:"+port, nil))
}