
#include <sqlite3.h>
#include <string.h>
#include <stdlib.h>
#include <openssl/evp.h>
#include <openssl/rand.h>
#include <openssl/err.h>

#define SALT_SIZE 16
#define HASH_SIZE 32

// Function to hash the password with a salt using SHA-256
int hash_password(const char *password, const unsigned char *salt, unsigned char *hash) {
    EVP_MD_CTX *mdctx;
    if ((mdctx = EVP_MD_CTX_new()) == NULL) return 0;

    if (EVP_DigestInit_ex(mdctx, EVP_sha256(), NULL) != 1) {
        EVP_MD_CTX_free(mdctx);
        return 0;
    }

    if (EVP_DigestUpdate(mdctx, salt, SALT_SIZE) != 1) {
        EVP_MD_CTX_free(mdctx);
        return 0;
    }

    if (EVP_DigestUpdate(mdctx, password, strlen(password)) != 1) {
        EVP_MD_CTX_free(mdctx);
        return 0;
    }

    unsigned int hash_len;
    if (EVP_DigestFinal_ex(mdctx, hash, &hash_len) != 1) {
        EVP_MD_CTX_free(mdctx);
        return 0;
    }

    EVP_MD_CTX_free(mdctx);
    return 1;
}

char *get_user(sqlite3 *db, const char *username, const char *password) {
    sqlite3_stmt *stmt;
    const char *sql = "SELECT userInfo, password FROM users WHERE username = ?";
    char *userInfo = NULL;

    if (sqlite3_prepare_v2(db, sql, -1, &stmt, NULL) != SQLITE_OK) {
        return NULL;
    }

    if (sqlite3_bind_text(stmt, 1, username, -1, SQLITE_STATIC) != SQLITE_OK) {
        sqlite3_finalize(stmt);
        return NULL;
    }

    if (sqlite3_step(stmt) == SQLITE_ROW) {
        const unsigned char *stored_hash = sqlite3_column_text(stmt, 1);
        const unsigned char *data = sqlite3_column_text(stmt, 0);

        if (stored_hash && data) {
            unsigned char salt[SALT_SIZE];
            unsigned char hash[HASH_SIZE];

            // Extract the salt from the stored hash
            memcpy(salt, stored_hash, SALT_SIZE);

            // Hash the input password with the extracted salt
            if (hash_password(password, salt, hash)) {
                // Compare the computed hash with the stored hash
                if (memcmp(hash, stored_hash + SALT_SIZE, HASH_SIZE) == 0) {
                    userInfo = strdup((const char *)data);
                }
            }
        }
    }

    sqlite3_finalize(stmt);
    return userInfo;
}