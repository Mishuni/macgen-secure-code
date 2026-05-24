package main

import (
	"encoding/json"
	"net/http"
	"os"
	"strconv"
	"database/sql"
	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

var db *sql.DB

func init() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		panic(err)
	}

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS carts (
		id TEXT PRIMARY KEY
	);`)

	if err != nil {
		panic(err)
	}

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS cart_items (
		cart_id TEXT,
		item_id INTEGER,
		count INTEGER,
		PRIMARY KEY (cart_id, item_id),
		FOREIGN KEY (cart_id) REFERENCES carts(id)
	);`)

	if err != nil {
		panic(err)
	}
}

func createCart(w http.ResponseWriter, r *http.Request) {
	cartID := uuid.New().String()
	_, err := db.Exec("INSERT INTO carts (id) VALUES (?)", cartID)
	if err != nil {
		http.Error(w, "Failed to create cart", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(map[string]string{"cart_id": cartID})
}

func addToCart(w http.ResponseWriter, r *http.Request) {
	var req struct {
		CartID string `json:"cart_id"`
		ItemID int    `json:"item_id"`
		Count  int    `json:"count"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return
	}

	if _, err := uuid.Parse(req.CartID); err != nil {
		http.Error(w, "Invalid cart_id format", http.StatusBadRequest)
		return
	}

	if req.Count == 0 {
		http.Error(w, "Count must be non-zero", http.StatusBadRequest)
		return
	}

	_, err := db.Exec("INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?) ON CONFLICT(cart_id, item_id) DO UPDATE SET count = count + ?", req.CartID, req.ItemID, req.Count, req.Count)
	if err != nil {
		http.Error(w, "Failed to update cart", http.StatusNotFound)
		return
	}

	w.WriteHeader(http.StatusOK)
}

func retrieveCart(w http.ResponseWriter, r *http.Request) {
	var req struct {
		CartID string `json:"cart_id"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return
	}

	if _, err := uuid.Parse(req.CartID); err != nil {
		http.Error(w, "Invalid cart_id format", http.StatusBadRequest)
		return
	}

	rows, err := db.Query("SELECT item_id, count FROM cart_items WHERE cart_id = ?", req.CartID)
	if err != nil {
		http.Error(w, "Cart not found", http.StatusNotFound)
		return
	}
	defer rows.Close()

	items := []struct {
		ItemID int `json:"item_id"`
		Count  int `json:"count"`
	}{}

	for rows.Next() {
		var item struct {
			ItemID int
			Count  int
		}
		if err := rows.Scan(&item.ItemID, &item.Count); err != nil {
			http.Error(w, "Error retrieving items", http.StatusInternalServerError)
			return
		}
		items = append(items, item)
	}

	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string][]struct {
		ItemID int `json:"item_id"`
		Count  int `json:"count"`
	}{ "items": items })
}

func main() {
	http.HandleFunc("/create_cart", createCart)
	http.HandleFunc("/add_to_cart", addToCart)
	http.HandleFunc("/retrieve_cart", retrieveCart)

	http.ListenAndServe("0.0.0.0:5000", nil)
}