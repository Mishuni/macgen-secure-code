#include <sqlite3.h>
#include <string.h>
#include <stdlib.h>
#include <bcrypt.h>

// Function to hash the password using bcrypt
int hash_password(const char *password, char *hashed_password, size_t hashed_password_len) {
    char salt[BCRYPT_HASHSIZE];
    
    // Generate a salt
    if (bcrypt_gensalt(12, salt) != 0) {
        return -1;
    }
    
    // Hash the password with the generated salt
    if (bcrypt_hashpw(password, salt, hashed_password) != 0) {
        return -1;
    }
    
    return 0;
}

char *get_user(sqlite3 *db, const char *username, const char *password) {
    if (!username || !password) {
        return NULL;
    }

    sqlite3_stmt *stmt;
    const char *sql = "SELECT userInfo, password FROM users WHERE username = ?";
    char *user_info = NULL;

    // Prepare the SQL statement
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, NULL) != SQLITE_OK) {
        return NULL;
    }

    // Bind the username to the SQL statement
    if (sqlite3_bind_text(stmt, 1, username, -1, SQLITE_TRANSIENT) != SQLITE_OK) {
        sqlite3_finalize(stmt);
        return NULL;
    }

    // Execute the query and check if a result is found
    if (sqlite3_step(stmt) == SQLITE_ROW) {
        const unsigned char *info = sqlite3_column_text(stmt, 0);
        const unsigned char *stored_password = sqlite3_column_text(stmt, 1);

        if (info && stored_password) {
            // Verify the password using bcrypt
            if (bcrypt_checkpw(password, (const char *)stored_password) == 0) {
                user_info = (char *)malloc(strlen((const char *)info) + 1);
                if (user_info) {
                    strcpy(user_info, (const char *)info);
                }
            }
        }
    }

    // Finalize the statement to release resources
    sqlite3_finalize(stmt);

    return user_info;
}