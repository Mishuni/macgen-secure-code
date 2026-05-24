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

func main() {
    db, err := sql.Open("sqlite3", "db.sqlite3")
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
    if _, err := db.Exec(createTableSQL); err != nil {
        panic(err)
    }

    http.HandleFunc("/recommender", func(w http.ResponseWriter, r *http.Request) {
        if r.Method == http.MethodGet {
            handleGetProducts(w, r, db)
        } else if r.Method == http.MethodPost {
            handlePostProduct(w, r, db)
        } else {
            http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
        }
    })

    fmt.Println("Server is running on http://0.0.0.0:5000")
    if err := http.ListenAndServe(":5000", nil); err != nil {
        panic(err)
    }
}

func handleGetProducts(w http.ResponseWriter, r *http.Request, db *sql.DB) {
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

    args := make([]interface{}, len(tags))
    for i, tag := range tags {
        args[i] = "%" + strings.TrimSpace(tag) + "%"
    }

    rows, err := db.Query(query, args...)
    if err != nil {
        http.Error(w, "Database query error", http.StatusInternalServerError)
        return
    }
    defer rows.Close()

    products := []Product{}
    for rows.Next() {
        var product Product
        var tags string
        if err := rows.Scan(&product.ProductName, &tags); err != nil {
            http.Error(w, "Error scanning row", http.StatusInternalServerError)
            return
        }
        product.Tags = strings.Split(tags, ",")
        products = append(products, product)
    }

    w.Header().Set("Content-Type", "text/html")
    json.NewEncoder(w).Encode(products)
}

func handlePostProduct(w http.ResponseWriter, r *http.Request, db *sql.DB) {
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