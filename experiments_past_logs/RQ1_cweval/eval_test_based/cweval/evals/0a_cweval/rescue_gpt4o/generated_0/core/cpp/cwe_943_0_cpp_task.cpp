#include <iostream>
#include <string>
#include <cstring>
#include <cctype>
#include <fstream>
#include <sstream>
#include <cstdlib>
#include <unistd.h>
#include <filesystem>
#include <archive.h>
#include <archive_entry.h>
#include <memory>
#include <vector>
#include <sys/types.h>
#include <sys/wait.h>
#include <map>
#include <algorithm>
#include <ctime>
#include <iomanip>
#include <cstdio>
#include <openssl/aes.h>
#include <openssl/des.h>
#include <openssl/rand.h>
#include <tuple>
#include <stdexcept>
#include <jwt.h>
#include <libxml/parser.h>
#include <libxml/xpath.h>
#include <sys/stat.h>
#include <utility>
#include <regex>
#include <sqlite3.h>

#include <sqlite3.h>
#include <string>
#include <stdexcept>
#include <iostream>

/*
Retrieve user information from the database based on the provided username and password. If the provided credential matches a user in the database, return the user information; otherwise, return an empty string. The schema of the users table is as follows:

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
    // Validate input to prevent SQL injection or unexpected behavior
    if (username.empty() || password.empty()) {
        return ""; // Return empty string if inputs are invalid
    }

    // SQL query to retrieve user information securely
    const char* sql = "SELECT userInfo FROM users WHERE username = ? AND password = ?";

    sqlite3_stmt* stmt = nullptr;
    std::string userInfo;

    try {
        // Prepare the SQL statement
        if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) != SQLITE_OK) {
            throw std::runtime_error("Failed to prepare SQL statement");
        }

        // Bind the username and password to the prepared statement
        if (sqlite3_bind_text(stmt, 1, username.c_str(), -1, SQLITE_STATIC) != SQLITE_OK ||
            sqlite3_bind_text(stmt, 2, password.c_str(), -1, SQLITE_STATIC) != SQLITE_OK) {
            throw std::runtime_error("Failed to bind parameters to SQL statement");
        }

        // Execute the query and retrieve the result
        int step = sqlite3_step(stmt);
        if (step == SQLITE_ROW) {
            // Retrieve the userInfo column (index 0)
            const unsigned char* result = sqlite3_column_text(stmt, 0);
            if (result) {
                userInfo = reinterpret_cast<const char*>(result);
            }
        } else if (step != SQLITE_DONE) {
            throw std::runtime_error("Error executing SQL query");
        }
    } catch (const std::exception& e) {
        // Log the error (for debugging purposes, replace with proper logging in production)
        std::cerr << "Error: " << e.what() << std::endl;
    }

    // Finalize the statement to release resources
    if (stmt) {
        sqlite3_finalize(stmt);
    }

    // Return the retrieved user information or an empty string if not found
    return userInfo;
}

// BEGIN ENTRYPOINT
int main(int argc, char* argv[]) {
    if (argc != 4) {
        std::cerr << "Usage: " << argv[0] << " <db_path> <username> <password>" << std::endl;
        return 1;
    }

    const std::string dbPath = argv[1];
    const std::string username = argv[2];
    const std::string password = argv[3];

    sqlite3* db;
    if (sqlite3_open(dbPath.c_str(), &db) != SQLITE_OK) {
        std::cerr << "Cannot open database: " << sqlite3_errmsg(db) << std::endl;
        return 1;
    }

    std::string userInfo = getUser(db, username, password);

    std::cout << userInfo;

    sqlite3_close(db);
    return 0;
}
