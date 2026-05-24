
package main

import (
    "database/sql"
    "log"

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