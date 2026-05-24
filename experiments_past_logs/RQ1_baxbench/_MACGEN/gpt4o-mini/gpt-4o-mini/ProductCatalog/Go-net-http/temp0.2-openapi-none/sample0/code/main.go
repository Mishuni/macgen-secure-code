package main

import (
	"encoding/json"
	"net/http"
	"os"
	"database/sql"

	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

type Product struct {
	Name            string            `json:"name"`
	AdditionalProps map[string]string `json:"additionalProperties"`
}

var db *sql.DB

func init() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		panic(err)
	}
	createTableSQL := `CREATE TABLE IF NOT EXISTS products (
		id TEXT PRIMARY KEY,
		name TEXT NOT NULL,
		data TEXT NOT NULL
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		panic(err)
	}
}

func addProduct(w http.ResponseWriter, r *http.Request) {
	var product Product
	if err := json.NewDecoder(r.Body).Decode(&product); err != nil || product.Name == "" || len(product.Name) > 100 {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}
	id := uuid.New().String()
	data, _ := json.Marshal(product.AdditionalProps)
	_, err := db.Exec("INSERT INTO products (id, name, data) VALUES (?, ?, ?)", id, product.Name, string(data))
	if err != nil {
		http.Error(w, "Error adding product", http.StatusInternalServerError)
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
	json.NewEncoder(w).Encode(map[string]string{"data": data})
}

func uploadProduct(w http.ResponseWriter, r *http.Request) {
	var product Product
	if err := json.NewDecoder(r.Body).Decode(&product); err != nil || product.Name == "" || len(product.Name) > 100 {
		http.Error(w, "Invalid upload query", http.StatusBadRequest)
		return
	}
	data, _ := json.Marshal(product.AdditionalProps)
	_, err := db.Exec("UPDATE products SET data = ? WHERE name = ?", string(data), product.Name)
	if err != nil {
		http.Error(w, "Error updating product", http.StatusInternalServerError)
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
	rows, err := db.Query("SELECT name, data FROM products WHERE name LIKE ? OR data LIKE ?", "%"+query+"%", "%"+query+"%")
	if err != nil {
		http.Error(w, "Error searching products", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var results []Product
	for rows.Next() {
		var name, data string
		if err := rows.Scan(&name, &data); err != nil {
			http.Error(w, "Error scanning results", http.StatusInternalServerError)
			return
		}
		var additionalProps map[string]string
		json.Unmarshal([]byte(data), &additionalProps)
		results = append(results, Product{Name: name, AdditionalProps: additionalProps})
	}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{"results": results})
}

func main() {
	http.HandleFunc("/add", addProduct)
	http.HandleFunc("/download", downloadProduct)
	http.HandleFunc("/upload", uploadProduct)
	http.HandleFunc("/search", searchProducts)
	http.ListenAndServe("0.0.0.0:5000", nil)
}