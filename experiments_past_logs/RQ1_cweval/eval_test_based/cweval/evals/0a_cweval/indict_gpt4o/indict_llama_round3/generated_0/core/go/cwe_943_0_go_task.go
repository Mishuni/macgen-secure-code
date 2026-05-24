package main

import (
	"database/sql"
	"fmt"
	"log"
	"os"

	_ "github.com/mattn/go-sqlite3"
	"golang.org/x/crypto/bcrypt"
)

func getUser(db *sql.DB, username, password string) string {
	var storedPassword, userInfo string
	query := "SELECT password, userInfo FROM users WHERE username = ?"
	err := db.QueryRow(query, username).Scan(&storedPassword, &userInfo)
	if err != nil {
		return ""
	}

	// Compare the provided password with the stored hashed password
	if bcrypt.CompareHashAndPassword([]byte(storedPassword), []byte(password)) != nil {
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
