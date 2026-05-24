package main

import (
	"encoding/json"
	"net/http"
	"os"
	"database/sql"
	"log"

	_ "github.com/mattn/go-sqlite3"
	"github.com/google/uuid"
)

type Product struct {
	Name string                 `json:"name"`
	Data map[string]interface{} `json:"data"`
}

var db *sql.DB

func init() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	createTable()
}

func createTable() {
	query := `CREATE TABLE IF NOT EXISTS products (
		id TEXT PRIMARY KEY,
		name TEXT NOT NULL UNIQUE,
		data TEXT NOT NULL
	);`
	_, err := db.Exec(query)
	if err != nil {
		log.Fatal(err)
	}
}

func addProduct(w http.ResponseWriter, r *http.Request) {
	var product Product
	if err := json.NewDecoder(r.Body).Decode(&product); err != nil || product.Name == "" {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}
	id := uuid.New().String()
	data, _ := json.Marshal(product.Data)
	_, err := db.Exec("INSERT INTO products (id, name, data) VALUES (?, ?, ?)", id, product.Name, data)
	if err != nil {
		http.Error(w, "Error adding product", http.StatusInternalServerError)
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
	w.Header().Set("Content-Type", "application/json")
	w.Write([]byte(`{"data":` + data + `}`))
}

func uploadProduct(w http.ResponseWriter, r *http.Request) {
	var product Product
	if err := json.NewDecoder(r.Body).Decode(&product); err != nil || product.Name == "" {
		http.Error(w, "Invalid upload query", http.StatusBadRequest)
		return
	}
	data, _ := json.Marshal(product.Data)
	_, err := db.Exec("UPDATE products SET data = ? WHERE name = ?", data, product.Name)
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
		var name string
		var data string
		if err := rows.Scan(&name, &data); err != nil {
			http.Error(w, "Error scanning results", http.StatusInternalServerError)
			return
		}
		var properties map[string]interface{}
		if err := json.Unmarshal([]byte(data), &properties); err != nil {
			http.Error(w, "Error parsing product data", http.StatusInternalServerError)
			return
		}
		results = append(results, Product{Name: name, Data: properties})
	}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{"results": results})
}

func main() {
	http.HandleFunc("/add", addProduct)
	http.HandleFunc("/download", downloadProduct)
	http.HandleFunc("/upload", uploadProduct)
	http.HandleFunc("/search", searchProducts)

	log.Println("Server started at :5000")
	if err := http.ListenAndServe(":5000", nil); err != nil {
		log.Fatal(err)
	}
}