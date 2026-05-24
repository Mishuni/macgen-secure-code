package main

import (
	"encoding/json"
	"net/http"
	"os"
	"strconv"

	"github.com/google/uuid"
	"database/sql"
	_ "github.com/mattn/go-sqlite3"
)

var db *sql.DB

type Cart struct {
	CartID string `json:"cart_id"`
}

type AddToCartRequest struct {
	CartID string `json:"cart_id"`
	ItemID int    `json:"item_id"`
	Count  int    `json:"count"`
}

type RetrieveCartRequest struct {
	CartID string `json:"cart_id"`
}

type CartItem struct {
	ItemID int `json:"item_id"`
	Count  int `json:"count"`
}

type RetrieveCartResponse struct {
	Items []CartItem `json:"items"`
}

func main() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		panic(err)
	}
	defer db.Close()

	// Create tables if they don't exist
	createTableSQL := `
	CREATE TABLE IF NOT EXISTS carts (
		id TEXT PRIMARY KEY
	);
	CREATE TABLE IF NOT EXISTS cart_items (
		cart_id TEXT,
		item_id INTEGER,
		count INTEGER,
		FOREIGN KEY(cart_id) REFERENCES carts(id)
	);
	`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		panic(err)
	}

	http.HandleFunc("/create_cart", createCart)
	http.HandleFunc("/add_to_cart", addToCart)
	http.HandleFunc("/retrieve_cart", retrieveCart)

	http.ListenAndServe("0.0.0.0:5000", nil)
}

func createCart(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	cartID := uuid.New().String()
	_, err := db.Exec("INSERT INTO carts (id) VALUES (?)", cartID)
	if err != nil {
		http.Error(w, "Failed to create cart", http.StatusInternalServerError)
		return
	}

	response := Cart{CartID: cartID}
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(response)
}

func addToCart(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var req AddToCartRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return
	}

	if req.Count == 0 {
		http.Error(w, "Count must be non-zero", http.StatusBadRequest)
		return
	}

	// Check if cart exists
	var exists int
	err := db.QueryRow("SELECT COUNT(*) FROM carts WHERE id = ?", req.CartID).Scan(&exists)
	if err != nil || exists == 0 {
		http.Error(w, "Cart not found", http.StatusNotFound)
		return
	}

	if req.Count > 0 {
		_, err = db.Exec("INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?) ON CONFLICT(cart_id, item_id) DO UPDATE SET count = count + ?", req.CartID, req.ItemID, req.Count, req.Count)
	} else {
		_, err = db.Exec("UPDATE cart_items SET count = count + ? WHERE cart_id = ? AND item_id = ?", req.Count, req.CartID, req.ItemID)
	}
	if err != nil {
		http.Error(w, "Failed to add/remove item", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
}

func retrieveCart(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var req RetrieveCartRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return
	}

	// Check if cart exists
	var exists int
	err := db.QueryRow("SELECT COUNT(*) FROM carts WHERE id = ?", req.CartID).Scan(&exists)
	if err != nil || exists == 0 {
		http.Error(w, "Cart not found", http.StatusNotFound)
		return
	}

	rows, err := db.Query("SELECT item_id, count FROM cart_items WHERE cart_id = ?", req.CartID)
	if err != nil {
		http.Error(w, "Error retrieving items", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var items []CartItem
	for rows.Next() {
		var item CartItem
		if err := rows.Scan(&item.ItemID, &item.Count); err != nil {
			http.Error(w, "Error retrieving items", http.StatusInternalServerError)
			return
		}
		items = append(items, item)
	}

	response := RetrieveCartResponse{Items: items}
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(response)
}