package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"strings"

	"github.com/google/uuid"
	"github.com/mattn/go-sqlite3"
)

var db *sqlite3.SQLiteConn

func init() {
	var err error
	db, err = sqlite3.Open("db.sqlite3")
	if err != nil {
		panic(err)
	}

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS products (
		id TEXT PRIMARY KEY,
		name TEXT NOT NULL,
		data TEXT NOT NULL
	)`)
	if err != nil {
		panic(err)
	}
}

func main() {
	http.HandleFunc("/add", addProduct)
	http.HandleFunc("/download", downloadProduct)
	http.HandleFunc("/upload", uploadProduct)
	http.HandleFunc("/search", searchProducts)

	fmt.Println("Server is running on port 5000...")
	http.ListenAndServe("0.0.0.0:5000", nil)
}

func addProduct(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var product map[string]interface{}
	if err := json.NewDecoder(r.Body).Decode(&product); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	name, ok := product["name"].(string)
	if !ok || name == "" {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	id := uuid.New().String()
	data, _ := json.Marshal(product)

	_, err := db.Exec("INSERT INTO products (id, name, data) VALUES (?, ?, ?)", id, name, string(data))
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
	w.Write([]byte(fmt.Sprintf(`{"data": %s}`, data)))
}

func uploadProduct(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var product map[string]interface{}
	if err := json.NewDecoder(r.Body).Decode(&product); err != nil {
		http.Error(w, "Invalid upload query", http.StatusBadRequest)
		return
	}

	name, ok := product["name"].(string)
	if !ok || name == "" {
		http.Error(w, "Invalid upload query", http.StatusBadRequest)
		return
	}

	data, _ := json.Marshal(product)

	_, err := db.Exec("REPLACE INTO products (name, data) VALUES (?, ?)", name, string(data))
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

	rows, err := db.Query("SELECT name, data FROM products WHERE name LIKE ? OR data LIKE ?", "%"+query+"%", "%"+query+"%")
	if err != nil {
		http.Error(w, "Failed to search products", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var results []map[string]interface{}
	for rows.Next() {
		var name, data string
		if err := rows.Scan(&name, &data); err != nil {
			http.Error(w, "Failed to read product", http.StatusInternalServerError)
			return
		}
		product := map[string]interface{}{"name": name}
		json.Unmarshal([]byte(data), &product)
		results = append(results, product)
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{"results": results})
}