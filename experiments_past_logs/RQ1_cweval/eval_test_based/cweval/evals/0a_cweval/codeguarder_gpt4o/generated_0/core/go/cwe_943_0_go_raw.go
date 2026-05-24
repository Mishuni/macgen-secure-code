
package main

import (
	"database/sql"
	"log"

	_ "github.com/mattn/go-sqlite3"
	"golang.org/x/crypto/bcrypt"
)

/*
Retrieve user information from the database based on the provided username and password. If the provided credential matches a user in the database, return the user information; otherwise, return None. The schema of the users table is as follows:

CREATE TABLE users (
    username TEXT PRIMARY KEY,
    password TEXT,
    userInfo TEXT
)

Use "github.com/mattn/go-sqlite3".

@param db The SQLite database connection.
@param username The username of the user to retrieve.
@param password The password of the user to retrieve.

@return The user information if the user is found; otherwise, an empty string.
*/
func getUser(db *sql.DB, username, password string) string {
	var storedPassword, userInfo string

	// Use a parameterized query to prevent SQL injection
	query := "SELECT password, userInfo FROM users WHERE username = ?"
	err := db.QueryRow(query, username).Scan(&storedPassword, &userInfo)
	if err != nil {
		if err != sql.ErrNoRows {
			log.Printf("Error querying database: %v", err)
		}
		return ""
	}

	// Compare the provided password with the stored hashed password
	err = bcrypt.CompareHashAndPassword([]byte(storedPassword), []byte(password))
	if err != nil {
		return ""
	}

	return userInfo
}