
package main

import (
	"database/sql"
	_ "github.com/mattn/go-sqlite3"
)

func getUser(db *sql.DB, username, password string) string {
	var userInfo string
	query := "SELECT userInfo FROM users WHERE username = ? AND password = ?"
	err := db.QueryRow(query, username, password).Scan(&userInfo)
	if err != nil {
		if err == sql.ErrNoRows {
			return ""
		}
		return ""
	}
	return userInfo
}