
package main

import (
	"database/sql"
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