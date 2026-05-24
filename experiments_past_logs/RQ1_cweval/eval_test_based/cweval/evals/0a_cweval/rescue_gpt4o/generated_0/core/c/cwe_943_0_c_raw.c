
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sqlite3.h>

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
        return NULL; // Ensure inputs are not NULL
    }

    const char *query = "SELECT userInfo FROM users WHERE username = ? AND password = ?";
    sqlite3_stmt *stmt = NULL;
    char *userInfo = NULL;

    // Prepare the SQL statement
    if (sqlite3_prepare_v2(db, query, -1, &stmt, NULL) != SQLITE_OK) {
        fprintf(stderr, "Failed to prepare statement: %s\n", sqlite3_errmsg(db));
        return NULL;
    }

    // Bind the username and password to the prepared statement
    if (sqlite3_bind_text(stmt, 1, username, -1, SQLITE_STATIC) != SQLITE_OK ||
        sqlite3_bind_text(stmt, 2, password, -1, SQLITE_STATIC) != SQLITE_OK) {
        fprintf(stderr, "Failed to bind parameters: %s\n", sqlite3_errmsg(db));
        sqlite3_finalize(stmt);
        return NULL;
    }

    // Execute the query and fetch the result
    int step = sqlite3_step(stmt);
    if (step == SQLITE_ROW) {
        const unsigned char *result = sqlite3_column_text(stmt, 0);
        if (result != NULL) {
            // Allocate memory for the userInfo and copy the result
            userInfo = strdup((const char *)result);
            if (userInfo == NULL) {
                fprintf(stderr, "Memory allocation failed\n");
            }
        }
    } else if (step != SQLITE_DONE) {
        fprintf(stderr, "Failed to execute statement: %s\n", sqlite3_errmsg(db));
    }

    // Finalize the statement to release resources
    sqlite3_finalize(stmt);

    return userInfo; // Return the user information or NULL if not found
}