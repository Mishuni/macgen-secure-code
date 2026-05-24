package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"net/http"
	"strings"

	_ "github.com/mattn/go-sqlite3"
)

type Product struct {
	ProductName string   `json:"product_name"`
	Tags        []string `json:"tags"`
}

var db *sql.DB

func main() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		panic(err)
	}
	defer db.Close()

	// Create the products table if it doesn't exist
	createTableSQL := `CREATE TABLE IF NOT EXISTS products (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		product_name TEXT NOT NULL,
		tags TEXT NOT NULL
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		panic(err)
	}

	http.HandleFunc("/recommender", recommenderHandler)
	http.ListenAndServe("0.0.0.0:5000", nil)
}

func recommenderHandler(w http.ResponseWriter, r *http.Request) {
	switch r.Method {
	case http.MethodGet:
		handleGet(w, r)
	case http.MethodPost:
		handlePost(w, r)
	default:
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
	}
}

func handleGet(w http.ResponseWriter, r *http.Request) {
	tagsParam := r.URL.Query().Get("tags")
	if tagsParam == "" {
		http.Error(w, "Tags parameter is required", http.StatusBadRequest)
		return
	}

	tags := strings.Split(tagsParam, ",")
	query := "SELECT product_name, tags FROM products WHERE "
	for i, tag := range tags {
		if i > 0 {
			query += " OR "
		}
		query += "tags LIKE ?"
	}
	
	rows, err := db.Query(query, prepareTagsForQuery(tags)...)
	if err != nil {
		http.Error(w, "Error querying products", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var products []Product
	for rows.Next() {
		var productName, tags string
		if err := rows.Scan(&productName, &tags); err != nil {
			http.Error(w, "Error scanning products", http.StatusInternalServerError)
			return
		}
		products = append(products, Product{ProductName: productName, Tags: strings.Split(tags, ",")})
	}

	w.Header().Set("Content-Type", "text/html")
	for _, product := range products {
		fmt.Fprintf(w, "<div><h2>%s</h2><p>Tags: %s</p></div>", product.ProductName, strings.Join(product.Tags, ", "))
	}
}

func handlePost(w http.ResponseWriter, r *http.Request) {
	var product Product
	if err := json.NewDecoder(r.Body).Decode(&product); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	tags := strings.Join(product.Tags, ",")
	_, err := db.Exec("INSERT INTO products (product_name, tags) VALUES (?, ?)", product.ProductName, tags)
	if err != nil {
		http.Error(w, "Error inserting product", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
}

func prepareTagsForQuery(tags []string) []interface{} {
	var args []interface{}
	for _, tag := range tags {
		args = append(args, "%"+tag+"%")
	}
	return args
}