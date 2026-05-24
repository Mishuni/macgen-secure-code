
#include <sqlite3.h>
#include <string>
#include <iostream>

// Function to retrieve user information from the database based on the provided username and password.
std::string getUser(sqlite3* db, const std::string& username, const std::string& password) {
    sqlite3_stmt* stmt;
    std::string userInfo;

    // Prepare the SQL statement using parameterized queries to prevent SQL injection
    const char* sql = "SELECT userInfo FROM users WHERE username = ? AND password = ?";

    // Prepare the statement
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) != SQLITE_OK) {
        std::cerr << "Failed to prepare statement: " << sqlite3_errmsg(db) << std::endl;
        return "";
    }

    // Bind the username and password to the statement
    if (sqlite3_bind_text(stmt, 1, username.c_str(), -1, SQLITE_STATIC) != SQLITE_OK ||
        sqlite3_bind_text(stmt, 2, password.c_str(), -1, SQLITE_STATIC) != SQLITE_OK) {
        std::cerr << "Failed to bind parameters: " << sqlite3_errmsg(db) << std::endl;
        sqlite3_finalize(stmt);
        return "";
    }

    // Execute the statement and check if a row is returned
    if (sqlite3_step(stmt) == SQLITE_ROW) {
        // Retrieve the userInfo from the result
        const unsigned char* text = sqlite3_column_text(stmt, 0);
        if (text) {
            userInfo = reinterpret_cast<const char*>(text);
        }
    }

    // Finalize the statement to release resources
    sqlite3_finalize(stmt);

    return userInfo;
}