package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"strings"

	_ "github.com/mattn/go-sqlite3"
)

var db *sql.DB

type Product struct {
	ProductName string   `json:"product_name"`
	Tags        []string `json:"tags"`
}

func init() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		panic(err)
	}

	createTableSQL := `CREATE TABLE IF NOT EXISTS products (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		product_name TEXT NOT NULL,
		tags TEXT NOT NULL
	);`
	if _, err = db.Exec(createTableSQL); err != nil {
		panic(err)
	}
}

func main() {
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
	tags := r.URL.Query().Get("tags")
	if tags == "" {
		http.Error(w, "Tags query parameter is required", http.StatusBadRequest)
		return
	}

	tagList := strings.Split(tags, ",")
	query := "SELECT product_name FROM products WHERE "
	for i, tag := range tagList {
		if i > 0 {
			query += " OR "
		}
		query += "tags LIKE ?"
	}
	
	rows, err := db.Query(query, prepareTags(tagList)...)
	if err != nil {
		http.Error(w, "Database query error", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var products []string
	for rows.Next() {
		var productName string
		if err := rows.Scan(&productName); err != nil {
			http.Error(w, "Error scanning results", http.StatusInternalServerError)
			return
		}
		products = append(products, productName)
	}

	w.Header().Set("Content-Type", "text/html")
	fmt.Fprintln(w, "<ul>")
	for _, product := range products {
		fmt.Fprintf(w, "<li>%s</li>", product)
	}
	fmt.Fprintln(w, "</ul>")
}

func handlePost(w http.ResponseWriter, r *http.Request) {
	var product Product
	if err := json.NewDecoder(r.Body).Decode(&product); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	if product.ProductName == "" || len(product.Tags) == 0 {
		http.Error(w, "Product name and tags are required", http.StatusBadRequest)
		return
	}

	tags := strings.Join(product.Tags, ",")
	_, err := db.Exec("INSERT INTO products (product_name, tags) VALUES (?, ?)", product.ProductName, tags)
	if err != nil {
		http.Error(w, "Database insert error", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
}

func prepareTags(tags []string) []interface{} {
	var args []interface{}
	for _, tag := range tags {
		args = append(args, "%"+tag+"%")
	}
	return args
}