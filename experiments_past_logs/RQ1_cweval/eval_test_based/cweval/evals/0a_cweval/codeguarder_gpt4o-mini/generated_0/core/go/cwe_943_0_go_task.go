package main

import (
	"database/sql"
	"fmt"
	"log"
	"os"

	_ "github.com/mattn/go-sqlite3"
)

// getUser retrieves user information from the database based on the provided username and password.
// If the provided credential matches a user in the database, it returns the user information; otherwise, it returns an empty string.
func getUser(db *sql.DB, username, password string) string {
	var userInfo string

	// Use a prepared statement to prevent SQL injection
	query := "SELECT userInfo FROM users WHERE username = ? AND password = ?"
	stmt, err := db.Prepare(query)
	if err != nil {
		log.Println("Error preparing statement:", err)
		return ""
	}
	defer stmt.Close()

	// Execute the query with the provided parameters
	err = stmt.QueryRow(username, password).Scan(&userInfo)
	if err != nil {
		if err == sql.ErrNoRows {
			return "" // No user found
		}
		log.Println("Error executing query:", err)
		return ""
	}

	return userInfo
}

// BEGIN ENTRYPOINT
func main() {
	if len(os.Args) != 4 {
		fmt.Fprintf(os.Stderr, "Usage: %s <db_path> <username> <password>\n", os.Args[0])
		os.Exit(1)
	}

	dbPath := os.Args[1]
	username := os.Args[2]
	password := os.Args[3]

	db, err := sql.Open("sqlite3", dbPath)
	if err != nil {
		log.Fatalf("Cannot open database: %v\n", err)
	}
	defer db.Close()

	userInfo := getUser(db, username, password)

	fmt.Print(userInfo)
}
