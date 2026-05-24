package main

import (
	"encoding/json"
	"net/http"
	"github.com/google/uuid"
	"database/sql"
	"log"
	_ "github.com/mattn/go-sqlite3"
)

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

var db *sql.DB

func init() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}

	createTableSQL := `CREATE TABLE IF NOT EXISTS carts (
		id TEXT PRIMARY KEY,
		item_id INTEGER,
		count INTEGER
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		log.Fatal(err)
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
	json.NewEncoder(w).Encode(Cart{CartID: cartID})
}

func addToCart(w http.ResponseWriter, r *http.Request) {
	var req AddToCartRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return
	}

	_, err := db.Exec("INSERT INTO carts (id, item_id, count) VALUES (?, ?, ?) ON CONFLICT(id, item_id) DO UPDATE SET count = count + ?", req.CartID, req.ItemID, req.Count, req.Count)
	if err != nil {
		http.Error(w, "Failed to add item to cart", http.StatusInternalServerError)
		return
	}
	w.WriteHeader(http.StatusOK)
}

func retrieveCart(w http.ResponseWriter, r *http.Request) {
	var req RetrieveCartRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return
	}

	rows, err := db.Query("SELECT item_id, count FROM carts WHERE id = ?", req.CartID)
	if err != nil {
		http.Error(w, "Failed to retrieve cart", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var items []CartItem
	for rows.Next() {
		var item CartItem
		if err := rows.Scan(&item.ItemID, &item.Count); err != nil {
			http.Error(w, "Failed to scan item", http.StatusInternalServerError)
			return
		}
		items = append(items, item)
	}

	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(RetrieveCartResponse{Items: items})
}

func main() {
	http.HandleFunc("/create_cart", createCart)
	http.HandleFunc("/add_to_cart", addToCart)
	http.HandleFunc("/retrieve_cart", retrieveCart)

	log.Println("Starting server on :5000")
	if err := http.ListenAndServe(":5000", nil); err != nil {
		log.Fatal(err)
	}
}