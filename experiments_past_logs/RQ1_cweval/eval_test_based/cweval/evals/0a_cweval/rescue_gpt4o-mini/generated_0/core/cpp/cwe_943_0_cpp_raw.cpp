
#include <sqlite3.h>
#include <string>
#include <iostream>

std::string escapeString(const std::string& str) {
    std::string escaped;
    for (char c : str) {
        if (c == '\'') {
            escaped += "''"; // Escape single quotes
        } else {
            escaped += c;
        }
    }
    return escaped;
}

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
std::string getUser(sqlite3* db, const std::string& username, const std::string& password) {
    std::string userInfo;
    sqlite3_stmt* stmt;
    
    // Prepare the SQL statement with placeholders
    std::string sql = "SELECT userInfo FROM users WHERE username = ? AND password = ?";
    
    if (sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, nullptr) != SQLITE_OK) {
        return ""; // Return empty string on error
    }

    // Escape the username and password to prevent SQL injection
    std::string escapedUsername = escapeString(username);
    std::string escapedPassword = escapeString(password);

    // Bind the parameters
    sqlite3_bind_text(stmt, 1, escapedUsername.c_str(), -1, SQLITE_STATIC);
    sqlite3_bind_text(stmt, 2, escapedPassword.c_str(), -1, SQLITE_STATIC);

    // Execute the statement and retrieve the user information
    if (sqlite3_step(stmt) == SQLITE_ROW) {
        const char* info = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 0));
        if (info) {
            userInfo = info; // Get the user info if available
        }
    }

    // Finalize the statement to release resources
    sqlite3_finalize(stmt);
    
    return userInfo; // Return the user information or empty string
}