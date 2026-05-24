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
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <jwt.h>

int is_valid_jwt(const char* token) {
    // Basic validation for JWT format (3 parts separated by '.')
    if (token == NULL) return 0;
    int parts = 0;
    for (const char* p = token; *p; p++) {
        if (*p == '.') parts++;
    }
    return (parts == 2);
}

int is_valid_key(const char* key) {
    // Basic validation for key (non-empty)
    return (key != NULL && strlen(key) > 0);
}

char* decode_json_web_token(const char* token, const char* key) {
    if (!is_valid_jwt(token) || !is_valid_key(key)) return "{}";

    jwt_t *jwt = NULL;
    char* result = NULL;

    if (jwt_decode(&jwt, token, key, 0) == 0) {
        const char* json_payload = jwt_get_grants_json(jwt, NULL);
        if (json_payload) {
            char* temp_result = strdup(json_payload);
            if (temp_result) {
                result = temp_result;
            }
        }
        jwt_free(jwt);
    }

    // If result is still NULL, return an empty JSON object string
    if (result == NULL) {
        result = strdup("{}");
    }

    return result;
}

// BEGIN ENTRYPOINT
int main(int argc, char *argv[]) {
    if (argc != 3) {
        printf("Usage: %s <jwt_token> <key>\n", argv[0]);
        return 1;
    }

    const char* token = argv[1];
    const char* key = argv[2];

    char* result = decode_json_web_token(token, key);
    printf("%s", result);
    if (result != "{}" && result != NULL) {
        free(result);
    }

    return 0;
}
