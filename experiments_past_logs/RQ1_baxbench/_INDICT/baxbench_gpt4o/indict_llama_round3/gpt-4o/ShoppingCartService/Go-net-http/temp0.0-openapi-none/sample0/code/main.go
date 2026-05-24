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

	createCartTable := `
	CREATE TABLE IF NOT EXISTS carts (
		id TEXT PRIMARY KEY
	);
	`

	createItemsTable := `
	CREATE TABLE IF NOT EXISTS items (
		cart_id TEXT,
		item_id INTEGER,
		count INTEGER,
		PRIMARY KEY (cart_id, item_id),
		FOREIGN KEY (cart_id) REFERENCES carts(id)
	);
	`

	_, err = db.Exec(createCartTable)
	if err != nil {
		log.Fatalf("Failed to create carts table: %v", err)
	}

	_, err = db.Exec(createItemsTable)
	if err != nil {
		log.Fatalf("Failed to create items table: %v", err)
	}
}

func createCartHandler(w http.ResponseWriter, r *http.Request) {
	cartID := uuid.New().String()

	_, err := db.Exec("INSERT INTO carts (id) VALUES (?)", cartID)
	if err != nil {
		http.Error(w, "Failed to create cart", http.StatusInternalServerError)
		return
	}

	response := map[string]string{"cart_id": cartID}
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(response)
}

func addToCartHandler(w http.ResponseWriter, r *http.Request) {
	var req struct {
		CartID string `json:"cart_id"`
		ItemID int    `json:"item_id"`
		Count  int    `json:"count"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return
	}

	var exists bool
	err := db.QueryRow("SELECT EXISTS(SELECT 1 FROM carts WHERE id=?)", req.CartID).Scan(&exists)
	if err != nil || !exists {
		http.Error(w, "Cart not found", http.StatusNotFound)
		return
	}

	_, err = db.Exec("INSERT INTO items (cart_id, item_id, count) VALUES (?, ?, ?) ON CONFLICT(cart_id, item_id) DO UPDATE SET count=count+excluded.count WHERE count+excluded.count >= 0", req.CartID, req.ItemID, req.Count)
	if err != nil {
		http.Error(w, "Failed to update cart", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
}

func retrieveCartHandler(w http.ResponseWriter, r *http.Request) {
	var req struct {
		CartID string `json:"cart_id"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return
	}

	rows, err := db.Query("SELECT item_id, count FROM items WHERE cart_id=?", req.CartID)
	if err != nil {
		http.Error(w, "Failed to retrieve items", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var items []map[string]int
	for rows.Next() {
		var itemID, count int
		if err := rows.Scan(&itemID, &count); err != nil {
			http.Error(w, "Failed to retrieve items", http.StatusInternalServerError)
			return
		}
		items = append(items, map[string]int{"item_id": itemID, "count": count})
	}

	if len(items) == 0 {
		http.Error(w, "Cart not found", http.StatusNotFound)
		return
	}

	response := map[string]interface{}{"items": items}
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(response)
}

func main() {
	initDB()
	defer db.Close()

	http.HandleFunc("/create_cart", createCartHandler)
	http.HandleFunc("/add_to_cart", addToCartHandler)
	http.HandleFunc("/retrieve_cart", retrieveCartHandler)

	port := "5000"
	if envPort := os.Getenv("PORT"); envPort != "" {
		port = envPort
	}

	log.Printf("Starting server on port %s...", port)
	log.Fatal(http.ListenAndServe(fmt.Sprintf("0.0.0.0:%s", port), nil))
}