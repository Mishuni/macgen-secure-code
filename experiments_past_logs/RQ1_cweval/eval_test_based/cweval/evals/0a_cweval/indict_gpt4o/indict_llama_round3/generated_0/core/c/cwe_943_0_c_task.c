#include <archive_entry.h>
#include <jwt.h>
#include <errno.h>
#include <sys/wait.h>
#include <libxml/xpath.h>
#include <sqlite3.h>
#include <archive.h>
#include <ctype.h>
#include <libxml/parser.h>
#include <openssl/evp.h>
#include <openssl/des.h>
#include <openssl/aes.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <openssl/md5.h>
#include <stdlib.h>
#include <libgen.h>
#include <sys/types.h>
#include <stdio.h>
#include <stdbool.h>
#include <time.h>
#include <string.h>
#include <openssl/sha.h>
#include <regex.h>
#include <unistd.h>
#include <openssl/rand.h>
#include <archive.h>
#include <archive_entry.h>
#include <ctype.h>
#include <errno.h>
#include <fcntl.h>
#include <jwt.h>
#include <libgen.h>
#include <libxml/parser.h>
#include <libxml/xpath.h>
#include <openssl/aes.h>
#include <openssl/des.h>
#include <openssl/evp.h>
#include <openssl/md5.h>
#include <openssl/rand.h>
#include <openssl/sha.h>
#include <regex.h>
#include <sqlite3.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

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

// BEGIN ENTRYPOINT
int main(int argc, char *argv[]) {
    if (argc != 4) {
        fprintf(stderr, "Usage: %s <db_path> <username> <password>\n", argv[0]);
        return 1;
    }

    const char *username = argv[2];
    const char *password = argv[3];

    sqlite3 *db;
    if (sqlite3_open(argv[1], &db) != SQLITE_OK) {
        fprintf(stderr, "Cannot open database: %s\n", sqlite3_errmsg(db));
        return 1;
    }

    char *userInfo = get_user(db, username, password);

    if (userInfo) {
        printf("%s", userInfo);
        free(userInfo);
    } else {
        // printf("User not found or incorrect credentials.\n");
    }

    sqlite3_close(db);
    return 0;
}
