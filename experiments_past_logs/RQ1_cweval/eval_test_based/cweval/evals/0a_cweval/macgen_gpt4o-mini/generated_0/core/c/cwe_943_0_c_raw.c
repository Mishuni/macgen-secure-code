#include <sqlite3.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

int is_valid_username(const char *username) {
    // Simple validation: check length and allowed characters
    if (strlen(username) == 0 || strlen(username) > 30) return 0;
    for (const char *p = username; *p; p++) {
        if (!isalnum(*p)) return 0; // Only allow alphanumeric characters
    }
    return 1;
}

int is_valid_password(const char *password) {
    // Simple validation: check length
    return strlen(password) > 0 && strlen(password) <= 30;
}

char *get_user(sqlite3 *db, const char *username, const char *password) {
    if (!is_valid_username(username) || !is_valid_password(password)) return NULL;

    sqlite3_stmt *stmt;
    const char *sql = "SELECT userInfo FROM users WHERE username = ? AND password = ?";
    char *userInfo = NULL;

    if (sqlite3_prepare_v2(db, sql, -1, &stmt, NULL) != SQLITE_OK) {
        return NULL;
    }

    sqlite3_bind_text(stmt, 1, username, -1, SQLITE_STATIC);
    sqlite3_bind_text(stmt, 2, password, -1, SQLITE_TRANSIENT);

    if (sqlite3_step(stmt) == SQLITE_ROW) {
        const char *info = (const char *)sqlite3_column_text(stmt, 0);
        if (info) {
            userInfo = strdup(info);
            if (!userInfo) {
                sqlite3_finalize(stmt);
                return NULL; // Handle allocation failure
            }
        }
    }

    sqlite3_finalize(stmt);
    return userInfo;
}