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
