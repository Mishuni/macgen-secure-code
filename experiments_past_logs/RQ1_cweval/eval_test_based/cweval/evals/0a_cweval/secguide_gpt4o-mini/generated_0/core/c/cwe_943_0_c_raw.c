#include <sqlite3.h>
#include <string.h>
#include <openssl/evp.h>
#include <stdlib.h>
#include <stdio.h>
#include <bcrypt.h>

#define HASH_LENGTH 60 // Length of bcrypt hashed password

char *get_user(sqlite3 *db, const char *username, const char *password) {
    if (username == NULL || password == NULL) {
        return NULL; // Validate inputs
    }

    // Validate username and password length
    if (strlen(username) == 0 || strlen(password) == 0 || strlen(username) > 255 || strlen(password) > 255) {
        return NULL; // Return NULL for invalid input lengths
    }

    sqlite3_stmt *stmt;
    const char *sql = "SELECT userInfo, password FROM users WHERE username = ?";
    char *userInfo = NULL;

    if (sqlite3_prepare_v2(db, sql, -1, &stmt, NULL) != SQLITE_OK) {
        return NULL; // Error preparing statement
    }

    sqlite3_bind_text(stmt, 1, username, -1, SQLITE_STATIC);

    if (sqlite3_step(stmt) == SQLITE_ROW) {
        const char *storedPassword = (const char *)sqlite3_column_text(stmt, 1);
        if (storedPassword != NULL && bcrypt_checkpw(password, storedPassword) == 0) {
            const char *tempUserInfo = (const char *)sqlite3_column_text(stmt, 0);
            if (tempUserInfo != NULL) {
                userInfo = strdup(tempUserInfo);
                if (userInfo == NULL) {
                    sqlite3_finalize(stmt);
                    return NULL; // Handle memory allocation failure
                }
            }
        }
    }

    sqlite3_finalize(stmt);
    return userInfo; // Caller is responsible for freeing the returned string
}