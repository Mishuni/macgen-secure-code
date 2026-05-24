package main

import (
	"database/sql"
	"encoding/json"
	"net/http"
	"strconv"

	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

type Cart struct {
	CartID string `json:"cart_id"`
}

type Item struct {
	ItemID int `json:"item_id"`
	Count  int `json:"count"`
}

type CartItems struct {
	Items []Item `json:"items"`
}

var db *sql.DB

func main() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		panic("Database error: " + err.Error())
	}
	defer db.Close()

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
	_, err := db.Exec("INSERT INTO carts (cart_id) VALUES (?)", cartID)
	if err != nil {
		http.Error(w, "Failed to create cart", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(Cart{CartID: cartID})
}

func addToCart(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
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

	// Validate ItemID and Count
	if req.ItemID <= 0 {
		http.Error(w, "Invalid item ID", http.StatusBadRequest)
		return
	}
	if req.Count < 0 {
		http.Error(w, "Count cannot be negative", http.StatusBadRequest)
		return
	}

	// Validate CartID format
	if _, err := uuid.Parse(req.CartID); err != nil {
		http.Error(w, "Invalid cart ID format", http.StatusBadRequest)
		return
	}

	if req.Count == 0 {
		_, err := db.Exec("DELETE FROM cart_items WHERE cart_id = ? AND item_id = ?", req.CartID, req.ItemID)
		if err != nil {
			http.Error(w, "Failed to remove item", http.StatusInternalServerError)
			return
		}
	} else {
		_, err := db.Exec("INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?) ON CONFLICT(cart_id, item_id) DO UPDATE SET count = count + ?", req.CartID, req.ItemID, req.Count, req.Count)
		if err != nil {
			http.Error(w, "Failed to add item", http.StatusInternalServerError)
			return
		}
	}

	w.WriteHeader(http.StatusOK)
}

func retrieveCart(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var req struct {
		CartID string `json:"cart_id"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	// Validate CartID format
	if _, err := uuid.Parse(req.CartID); err != nil {
		http.Error(w, "Invalid cart ID format", http.StatusBadRequest)
		return
	}

	rows, err := db.Query("SELECT item_id, count FROM cart_items WHERE cart_id = ?", req.CartID)
	if err != nil {
		http.Error(w, "Failed to retrieve cart", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var items []Item
	for rows.Next() {
		var item Item
		if err := rows.Scan(&item.ItemID, &item.Count); err != nil {
			http.Error(w, "Failed to scan item", http.StatusInternalServerError)
			return
		}
		items = append(items, item)
	}

	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(CartItems{Items: items})
}