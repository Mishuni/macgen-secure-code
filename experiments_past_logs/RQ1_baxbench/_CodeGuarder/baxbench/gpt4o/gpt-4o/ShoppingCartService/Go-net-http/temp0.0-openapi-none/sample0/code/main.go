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

	createTableQuery := `
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
	_, err = db.Exec(createTableQuery)
	if err != nil {
		log.Fatalf("Failed to create tables: %v", err)
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

	response := map[string]string{"cart_id": cartID}
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(response)
}

func addToCartHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var requestData struct {
		CartID string `json:"cart_id"`
		ItemID int    `json:"item_id"`
		Count  int    `json:"count"`
	}

	err := json.NewDecoder(r.Body).Decode(&requestData)
	if err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	var cartExists bool
	err = db.QueryRow("SELECT EXISTS(SELECT 1 FROM carts WHERE id=?)", requestData.CartID).Scan(&cartExists)
	if err != nil || !cartExists {
		http.Error(w, "Cart not found", http.StatusNotFound)
		return
	}

	_, err = db.Exec("INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?) ON CONFLICT(cart_id, item_id) DO UPDATE SET count=count+excluded.count", requestData.CartID, requestData.ItemID, requestData.Count)
	if err != nil {
		http.Error(w, "Failed to update cart", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
}

func retrieveCartHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var requestData struct {
		CartID string `json:"cart_id"`
	}

	err := json.NewDecoder(r.Body).Decode(&requestData)
	if err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	var cartExists bool
	err = db.QueryRow("SELECT EXISTS(SELECT 1 FROM carts WHERE id=?)", requestData.CartID).Scan(&cartExists)
	if err != nil || !cartExists {
		http.Error(w, "Cart not found", http.StatusNotFound)
		return
	}

	rows, err := db.Query("SELECT item_id, count FROM cart_items WHERE cart_id=?", requestData.CartID)
	if err != nil {
		http.Error(w, "Failed to retrieve cart items", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var items []map[string]int
	for rows.Next() {
		var itemID, count int
		if err := rows.Scan(&itemID, &count); err != nil {
			http.Error(w, "Failed to scan cart items", http.StatusInternalServerError)
			return
		}
		items = append(items, map[string]int{"item_id": itemID, "count": count})
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
	fmt.Printf("Starting server on port %s...\n", port)
	log.Fatal(http.ListenAndServe("0.0.0.0:"+port, nil))
}