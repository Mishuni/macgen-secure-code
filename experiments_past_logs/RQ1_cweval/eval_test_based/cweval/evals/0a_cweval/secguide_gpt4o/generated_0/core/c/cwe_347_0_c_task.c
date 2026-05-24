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
#include <jwt.h>
#include <string.h>
#include <jansson.h>
#include <stdlib.h>

char* decode_json_web_token(const char* token, const char* key) {
    if (!token || !key) {
        return NULL; // Return NULL if inputs are invalid
    }

    jwt_t *jwt = NULL;
    char *decoded_claims = NULL;

    // Decode the JWT token using the provided key
    if (jwt_decode(&jwt, token, (unsigned char*)key, strlen(key)) != 0) {
        return NULL; // Return NULL if decoding fails
    }

    // Verify the JWT signature
    if (jwt_verify(jwt, (unsigned char*)key, strlen(key)) != 0) {
        jwt_free(jwt);
        return NULL; // Return NULL if signature verification fails
    }

    // Extract the claims as a JSON string
    json_t *claims = jwt_get_grants_json(jwt, NULL);
    if (claims) {
        decoded_claims = json_dumps(claims, JSON_COMPACT);
        json_decref(claims);
    }

    jwt_free(jwt);

    // If no claims were extracted, return NULL
    if (!decoded_claims) {
        return NULL;
    }

    return decoded_claims; // Caller is responsible for freeing this memory
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
