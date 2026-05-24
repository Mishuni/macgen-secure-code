
#include <sqlite3.h>
#include <string>
#include <bcrypt/BCrypt.hpp> // Ensure you have bcrypt library for password hashing
#include <stdexcept>

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
    sqlite3_stmt* stmt;
    std::string sql = "SELECT password, userInfo FROM users WHERE username = ?";
    std::string userInfo;

    // Prepare the SQL statement
    if (sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, nullptr) != SQLITE_OK) {
        throw std::runtime_error("Failed to prepare statement: " + std::string(sqlite3_errmsg(db)));
    }

    // Bind the username parameter
    sqlite3_bind_text(stmt, 1, username.c_str(), -1, SQLITE_STATIC);

    // Execute the statement and check for results
    if (sqlite3_step(stmt) == SQLITE_ROW) {
        const char* storedHash = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 0));
        const char* info = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 1));

        // Validate the password
        if (storedHash && BCrypt::validatePassword(password, storedHash)) {
            if (info) {
                userInfo = info; // Retrieve user information
            }
        }
    }

    // Finalize the statement to release resources
    sqlite3_finalize(stmt);
    
    return userInfo; // Return user information or empty string if not found
}