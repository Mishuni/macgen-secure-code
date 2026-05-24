package main

import (
	"database/sql"
	"encoding/json"
	"log"
	"net/http"
	"os"

	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

var db *sql.DB

func main() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	// Initialize database schema
	initDB()

	http.HandleFunc("/create_cart", createCartHandler)
	http.HandleFunc("/add_to_cart", addToCartHandler)
	http.HandleFunc("/retrieve_cart", retrieveCartHandler)

	log.Println("Starting server on 0.0.0.0:5000...")
	log.Fatal(http.ListenAndServe("0.0.0.0:5000", nil))
}

func initDB() {
	_, err := db.Exec(`
		CREATE TABLE IF NOT EXISTS carts (
			id TEXT PRIMARY KEY
		);
		CREATE TABLE IF NOT EXISTS cart_items (
			cart_id TEXT,
			item_id INTEGER,
			count INTEGER,
			PRIMARY KEY (cart_id, item_id),
			FOREIGN KEY (cart_id) REFERENCES carts(id)
		);
	`)
	if err != nil {
		log.Fatalf("Failed to initialize database: %v", err)
	}
}

func createCartHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

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
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req struct {
		CartID string `json:"cart_id"`
		ItemID int    `json:"item_id"`
		Count  int    `json:"count"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	// Check if cart exists
	var exists bool
	err := db.QueryRow("SELECT EXISTS(SELECT 1 FROM carts WHERE id = ?)", req.CartID).Scan(&exists)
	if err != nil || !exists {
		http.Error(w, "Cart not found", http.StatusNotFound)
		return
	}

	// Update or insert item in cart
	_, err = db.Exec(`
		INSERT INTO cart_items (cart_id, item_id, count)
		VALUES (?, ?, ?)
		ON CONFLICT(cart_id, item_id) DO UPDATE SET count = count + excluded.count
	`, req.CartID, req.ItemID, req.Count)
	if err != nil {
		http.Error(w, "Failed to update cart", http.StatusInternalServerError)
		return
	}

	// Remove items with count <= 0
	_, err = db.Exec("DELETE FROM cart_items WHERE cart_id = ? AND item_id = ? AND count <= 0", req.CartID, req.ItemID)
	if err != nil {
		http.Error(w, "Failed to clean up cart", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
}

func retrieveCartHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req struct {
		CartID string `json:"cart_id"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	// Check if cart exists
	var exists bool
	err := db.QueryRow("SELECT EXISTS(SELECT 1 FROM carts WHERE id = ?)", req.CartID).Scan(&exists)
	if err != nil || !exists {
		http.Error(w, "Cart not found", http.StatusNotFound)
		return
	}

	// Retrieve items in the cart
	rows, err := db.Query("SELECT item_id, count FROM cart_items WHERE cart_id = ?", req.CartID)
	if err != nil {
		http.Error(w, "Failed to retrieve cart items", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var items []map[string]interface{}
	for rows.Next() {
		var itemID, count int
		if err := rows.Scan(&itemID, &count); err != nil {
			http.Error(w, "Failed to parse cart items", http.StatusInternalServerError)
			return
		}
		items = append(items, map[string]interface{}{
			"item_id": itemID,
			"count":   count,
		})
	}

	response := map[string]interface{}{"items": items}
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(response)
}