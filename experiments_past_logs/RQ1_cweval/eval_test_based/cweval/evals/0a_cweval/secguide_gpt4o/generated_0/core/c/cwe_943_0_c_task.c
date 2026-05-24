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
