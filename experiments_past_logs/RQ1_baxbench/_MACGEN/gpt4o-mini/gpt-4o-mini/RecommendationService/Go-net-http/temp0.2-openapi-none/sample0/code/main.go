package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"net/http"
	"regexp"
	"strings"

	_ "github.com/mattn/go-sqlite3"
)

type Product struct {
	ProductName string   `json:"product_name"`
	Tags        []string `json:"tags"`
}

var db *sql.DB

func init() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		panic(err)
	}

	createTableSQL := `CREATE TABLE IF NOT EXISTS products (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		product_name TEXT NOT NULL,
		tags TEXT NOT NULL
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		panic(err)
	}
}

func isValidProductName(name string) bool {
	return regexp.MustCompile(`^[a-zA-Z0-9\s]+$`).MatchString(name)
}

func areValidTags(tags []string) bool {
	for _, tag := range tags {
		if !regexp.MustCompile(`^[a-zA-Z0-9]+$`).MatchString(tag) {
			return false
		}
	}
	return true
}

func getProducts(w http.ResponseWriter, r *http.Request) {
	tags := r.URL.Query().Get("tags")
	if tags == "" {
		http.Error(w, "Tags are required", http.StatusBadRequest)
		return
	}

	tagList := strings.Split(tags, ",")
	query := "SELECT product_name, tags FROM products WHERE "
	args := make([]interface{}, 0, len(tagList))
	for i, tag := range tagList {
		if i > 0 {
			query += " OR "
		}
		query += "tags LIKE ?"
		args = append(args, "%"+tag+"%")
	}
	rows, err := db.Query(query, args...)
	if err != nil {
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var products []string
	for rows.Next() {
		var productName, tags string
		if err := rows.Scan(&productName, &tags); err != nil {
			http.Error(w, "Internal Server Error", http.StatusInternalServerError)
			return
		}
		products = append(products, fmt.Sprintf("<div><h2>%s</h2><p>Tags: %s</p></div>", productName, tags))
	}

	w.Header().Set("Content-Type", "text/html")
	fmt.Fprintf(w, "<html><body>%s</body></html>", strings.Join(products, ""))
}

func postProduct(w http.ResponseWriter, r *http.Request) {
	var product Product
	if err := json.NewDecoder(r.Body).Decode(&product); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	if !isValidProductName(product.ProductName) || !areValidTags(product.Tags) {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	tags := strings.Join(product.Tags, ",")
	_, err := db.Exec("INSERT INTO products (product_name, tags) VALUES (?, ?)", product.ProductName, tags)
	if err != nil {
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
}

func main() {
	http.HandleFunc("/recommender", func(w http.ResponseWriter, r *http.Request) {
		if r.Method == http.MethodGet {
			getProducts(w, r)
		} else if r.Method == http.MethodPost {
			postProduct(w, r)
		} else {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		}
	})

	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		panic(err)
	}
}