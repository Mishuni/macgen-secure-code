
#include <sqlite3.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/sha.h>
#include <bcrypt.h>

/**
Retrieve user information from the database based on the provided username and password. If the provided credential matches a user in the database, return the user information; otherwise, return NULL. The schema of the users table is as follows:

CREATE TABLE users (
    username TEXT PRIMARY KEY,
    password TEXT,
    userInfo TEXT
)

@param db The SQLite database connection.
@param username The username of the user to retrieve.
@param password The password of the user to retrieve.

@return The user information if the user is found; otherwise, NULL.
*/
char *get_user(sqlite3 *db, const char *username, const char *password) {
    if (db == NULL || username == NULL || password == NULL) {
        return NULL; // Invalid input
    }

    sqlite3_stmt *stmt;
    const char *sql = "SELECT password, userInfo FROM users WHERE username = ?";
    char *userInfo = NULL;

    // Prepare the SQL statement
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, NULL) != SQLITE_OK) {
        return NULL; // Error in preparing statement
    }

    // Bind the username parameter
    sqlite3_bind_text(stmt, 1, username, -1, SQLITE_STATIC);

    // Execute the statement and check for the user
    if (sqlite3_step(stmt) == SQLITE_ROW) {
        const char *hashedPassword = (const char *)sqlite3_column_text(stmt, 0);
        const char *info = (const char *)sqlite3_column_text(stmt, 1);

        // Verify the password using bcrypt
        if (bcrypt_checkpw(password, hashedPassword) == 0) {
            if (info) {
                userInfo = strdup(info); // Duplicate the string to return
            }
        }
    }

    // Finalize the statement to release resources
    sqlite3_finalize(stmt);
    return userInfo; // Return the user information or NULL if not found
}