package main

import (
	"database/sql"
	_ "github.com/mattn/go-sqlite3"
	"golang.org/x/crypto/bcrypt"
)

func getUser(db *sql.DB, username, password string) string {
	var storedHash string
	query := "SELECT password FROM users WHERE username = ?"
	err := db.QueryRow(query, username).Scan(&storedHash)

	// If the user does not exist, return an empty string
	if err == sql.ErrNoRows {
		return ""
	} else if err != nil {
		return ""
	}

	// Compare the provided password with the stored hash
	if err := bcrypt.CompareHashAndPassword([]byte(storedHash), []byte(password)); err != nil {
		return ""
	}

	var userInfo string
	query = "SELECT userInfo FROM users WHERE username = ?"
	err = db.QueryRow(query, username).Scan(&userInfo)
	if err != nil {
		return ""
	}

	return userInfo
}