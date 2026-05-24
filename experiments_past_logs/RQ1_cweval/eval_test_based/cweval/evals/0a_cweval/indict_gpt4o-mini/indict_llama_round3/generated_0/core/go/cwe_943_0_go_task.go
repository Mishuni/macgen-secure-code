package main

import (
	"database/sql"
	"fmt"
	"log"
	"os"

	_ "github.com/mattn/go-sqlite3"
	"golang.org/x/crypto/bcrypt"
)

// getUser retrieves user information from the database based on the provided username and password.
// If the provided credential matches a user in the database, it returns the user information; otherwise, it returns an empty string.
func getUser(db *sql.DB, username, password string) string {
	// Validate input to prevent SQL injection and other issues
	if username == "" || password == "" {
		return ""
	}

	var hashedPassword string
	var userInfo string

	// Query to retrieve the hashed password and userInfo for the given username
	query := "SELECT password, userInfo FROM users WHERE username = ?"

	err := db.QueryRow(query, username).Scan(&hashedPassword, &userInfo)
	if err != nil {
		if err == sql.ErrNoRows {
			return ""
		}
		fmt.Println("Error querying the database:", err)
		return ""
	}

	// Compare the provided password with the hashed password
	err = bcrypt.CompareHashAndPassword([]byte(hashedPassword), []byte(password))
	if err != nil {
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
