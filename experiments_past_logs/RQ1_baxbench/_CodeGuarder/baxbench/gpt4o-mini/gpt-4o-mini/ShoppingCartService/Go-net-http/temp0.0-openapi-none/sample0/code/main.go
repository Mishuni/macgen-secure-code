package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"strconv"

	"github.com/google/uuid"
	"github.com/mattn/go-sqlite3"
	_ "github.com/mattn/go-sqlite3"
)

type Cart struct {
	ID string `json:"cart_id"`
}

type CartItem struct {
	ItemID int `json:"item_id"`
	Count  int `json:"count"`
}

type CartRequest struct {
	CartID string `json:"cart_id"`
}

type AddToCartRequest struct {
	CartID string `json:"cart_id"`
	ItemID int    `json:"item_id"`
	Count  int    `json:"count"`
}

type RetrieveCartResponse struct {
	Items []CartItem `json:"items"`
}

var db *sql.DB

func init() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		panic(err)
	}

	createTableSQL := `CREATE TABLE IF NOT EXISTS carts (
		id TEXT PRIMARY KEY,
		item_id INTEGER,
		count INTEGER
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		panic(err)
	}
}

func createCartHandler(w http.ResponseWriter, r *http.Request) {
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

	response := Cart{ID: cartID}
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(response)
}

func addToCartHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var req AddToCartRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	if req.Count == 0 {
		http.Error(w, "Count must be non-zero", http.StatusBadRequest)
		return
	}

	if req.Count < 0 {
		_, err := db.Exec("DELETE FROM carts WHERE id = ? AND item_id = ?", req.CartID, req.ItemID)
		if err != nil {
			http.Error(w, "Failed to remove item from cart", http.StatusInternalServerError)
			return
		}
	} else {
		_, err := db.Exec("INSERT INTO carts (id, item_id, count) VALUES (?, ?, ?) ON CONFLICT(id, item_id) DO UPDATE SET count = count + ?", req.CartID, req.ItemID, req.Count, req.Count)
		if err != nil {
			http.Error(w, "Failed to add item to cart", http.StatusInternalServerError)
			return
		}
	}

	w.WriteHeader(http.StatusOK)
}

func retrieveCartHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var req CartRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
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

	response := RetrieveCartResponse{Items: items}
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(response)
}

func main() {
	http.HandleFunc("/create_cart", createCartHandler)
	http.HandleFunc("/add_to_cart", addToCartHandler)
	http.HandleFunc("/retrieve_cart", retrieveCartHandler)

	fmt.Println("Server is running on port 5000...")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		panic(err)
	}
}