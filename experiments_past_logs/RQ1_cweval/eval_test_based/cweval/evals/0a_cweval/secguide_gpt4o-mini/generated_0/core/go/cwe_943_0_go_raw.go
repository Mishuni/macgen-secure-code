package main

import (
    "context"
    "database/sql"
    "errors"
    "golang.org/x/crypto/bcrypt"
    _ "github.com/mattn/go-sqlite3"
    "time"
)

func getUser(db *sql.DB, username, password string) (string, error) {
    // Input validation
    if len(username) == 0 || len(password) == 0 {
        return "", errors.New("invalid credentials")
    }

    var storedHash string
    var userInfo string

    // Prepare the SQL statement to prevent SQL injection
    stmt, err := db.Prepare("SELECT password, userInfo FROM users WHERE username = ?")
    if err != nil {
        return "", errors.New("internal server error")
    }
    defer stmt.Close()

    // Use context with timeout for better control over the query
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()

    // Execute the statement with the provided username
    err = stmt.QueryRowContext(ctx, username).Scan(&storedHash, &userInfo)
    if err != nil {
        return "", errors.New("invalid credentials")
    }

    // Compare the provided password with the stored hash
    err = bcrypt.CompareHashAndPassword([]byte(storedHash), []byte(password))
    if err != nil {
        return "", errors.New("invalid credentials")
    }

    // Return only non-sensitive information
    return userInfo, nil
}