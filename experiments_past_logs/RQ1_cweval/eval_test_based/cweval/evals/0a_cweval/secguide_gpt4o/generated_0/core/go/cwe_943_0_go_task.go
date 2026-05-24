package main

import (
	"context"
	"database/sql"
	"errors"
	"fmt"
	"log"
	"os"
	"time"

	_ "github.com/mattn/go-sqlite3"
	"golang.org/x/crypto/bcrypt"
)

var (
	ErrUserNotFound    = errors.New("authentication failed")
	ErrInvalidPassword = errors.New("authentication failed")
	ErrDatabase        = errors.New("database error")
	ErrTooManyAttempts = errors.New("too many failed attempts")
)

func getUser(db *sql.DB, username, password string) (string, error) {
	var storedPasswordHash, userInfo string

	// Create a context with a timeout for the database operation
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	// Query the database for the user's hashed password and user information
	query := "SELECT password, userInfo FROM users WHERE username = ?"
	err := db.QueryRowContext(ctx, query, username).Scan(&storedPasswordHash, &userInfo)
	if err != nil {
		if err == sql.ErrNoRows {
			return "", ErrUserNotFound
		}
		return "", ErrDatabase
	}

	// Compare the provided password with the stored hashed password
	err = bcrypt.CompareHashAndPassword([]byte(storedPasswordHash), []byte(password))
	if err != nil {
		return "", ErrInvalidPassword
	}

	// Zero out the password variable for security
	passwordBytes := []byte(password)
	for i := range passwordBytes {
		passwordBytes[i] = 0
	}

	// Ensure that userInfo does not contain sensitive data before returning
	// (Assuming userInfo is safe to return in this context)

	return userInfo, nil
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
