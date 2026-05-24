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
		log.Fatal(err)
	}

	createTableSQL := `CREATE TABLE IF NOT EXISTS products (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		name TEXT NOT NULL UNIQUE,
		properties TEXT
	);`

	_, err = db.Exec(createTableSQL)
	if err != nil {
		log.Fatal(err)
	}
}

func addProductHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var product map[string]string
	err := json.NewDecoder(r.Body).Decode(&product)
	if err != nil || product["name"] == "" {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	properties, err := json.Marshal(product)
	if err != nil {
		http.Error(w, "Error processing properties", http.StatusInternalServerError)
		return
	}

	_, err = db.Exec("INSERT INTO products (name, properties) VALUES (?, ?)", product["name"], string(properties))
	if err != nil {
		http.Error(w, "Error adding product", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusCreated)
}

func downloadProductHandler(w http.ResponseWriter, r *http.Request) {
	name := r.URL.Query().Get("name")
	if name == "" {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	row := db.QueryRow("SELECT properties FROM products WHERE name = ?", name)
	var properties string
	err := row.Scan(&properties)
	if err != nil {
		http.Error(w, "Product not found", http.StatusNotFound)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{"data": properties})
}

func uploadProductHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var product map[string]string
	err := json.NewDecoder(r.Body).Decode(&product)
	if err != nil || product["name"] == "" || product["data"] == "" {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	_, err = db.Exec("UPDATE products SET properties = ? WHERE name = ?", product["data"], product["name"])
	if err != nil {
		http.Error(w, "Error updating product", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
}

func searchProductHandler(w http.ResponseWriter, r *http.Request) {
	query := r.URL.Query().Get("query")
	if query == "" {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	rows, err := db.Query("SELECT properties FROM products WHERE properties LIKE ?", "%"+query+"%")
	if err != nil {
		http.Error(w, "Error searching products", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var results []map[string]string
	for rows.Next() {
		var properties string
		err := rows.Scan(&properties)
		if err != nil {
			http.Error(w, "Error processing results", http.StatusInternalServerError)
			return
		}

		var product map[string]string
		err = json.Unmarshal([]byte(properties), &product)
		if err != nil {
			http.Error(w, "Error processing results", http.StatusInternalServerError)
			return
		}

		results = append(results, product)
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{"results": results})
}

func main() {
	initDB()
	defer db.Close()

	http.HandleFunc("/add", addProductHandler)
	http.HandleFunc("/download", downloadProductHandler)
	http.HandleFunc("/upload", uploadProductHandler)
	http.HandleFunc("/search", searchProductHandler)

	fmt.Println("Server is running on port 5000")
	log.Fatal(http.ListenAndServe("0.0.0.0:5000", nil))
}