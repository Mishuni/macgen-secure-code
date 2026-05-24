package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"regexp"
	"sync"

	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

var (
	db   *sql.DB
	once sync.Once
)

func initDB() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to open database: %v", err)
	}

	createTableQueries := []string{
		`CREATE TABLE IF NOT EXISTS carts (id TEXT PRIMARY KEY)`,
		`CREATE TABLE IF NOT EXISTS cart_items (cart_id TEXT, item_id INTEGER, count INTEGER, PRIMARY KEY (cart_id, item_id))`,
	}

	for _, query := range createTableQueries {
		if _, err := db.Exec(query); err != nil {
			log.Fatalf("Failed to create table: %v", err)
		}
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
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(map[string]string{"cart_id": cartID})
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
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return
	}

	if !isValidUUID(req.CartID) || req.ItemID <= 0 || req.Count <= 0 {
		http.Error(w, "Invalid input data", http.StatusBadRequest)
		return
	}

	var exists bool
	err := db.QueryRow("SELECT EXISTS(SELECT 1 FROM carts WHERE id=?)", req.CartID).Scan(&exists)
	if err != nil || !exists {
		http.Error(w, "Cart not found", http.StatusNotFound)
		return
	}

	_, err = db.Exec("INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?) ON CONFLICT(cart_id, item_id) DO UPDATE SET count=count+excluded.count", req.CartID, req.ItemID, req.Count)
	if err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
}

func retrieveCartHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req struct {
		CartID string `json:"cart_id"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return
	}

	if !isValidUUID(req.CartID) {
		http.Error(w, "Invalid cart ID", http.StatusBadRequest)
		return
	}

	rows, err := db.Query("SELECT item_id, count FROM cart_items WHERE cart_id=?", req.CartID)
	if err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var items []map[string]int
	for rows.Next() {
		var itemID, count int
		if err := rows.Scan(&itemID, &count); err != nil {
			http.Error(w, "Internal server error", http.StatusInternalServerError)
			return
		}
		items = append(items, map[string]int{"item_id": itemID, "count": count})
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]interface{}{"items": items})
}

func isValidUUID(u string) bool {
	r := regexp.MustCompile("^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$")
	return r.MatchString(u)
}

func main() {
	once.Do(initDB)

	http.HandleFunc("/create_cart", createCartHandler)
	http.HandleFunc("/add_to_cart", addToCartHandler)
	http.HandleFunc("/retrieve_cart", retrieveCartHandler)

	port := "5000"
	if envPort := os.Getenv("PORT"); envPort != "" {
		port = envPort
	}

	log.Printf("Starting server on port %s", port)
	if err := http.ListenAndServe(fmt.Sprintf("0.0.0.0:%s", port), nil); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}