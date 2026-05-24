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
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define MAX_USER_ID_LENGTH 256 // Define a maximum length for user_id

// Function to URL encode a string
char* url_encode(const char* str) {
    if (str == NULL) return NULL;

    size_t len = strlen(str);
    size_t encoded_len = 0;

    // Calculate the length of the encoded string
    for (size_t i = 0; i < len; i++) {
        if (isalnum((unsigned char)str[i]) || strchr("-_.~", str[i])) {
            encoded_len++;
        } else {
            encoded_len += 3; // For '%' and two hex digits
        }
    }

    char* encoded = (char*)malloc(encoded_len + 1);
    if (encoded == NULL) return NULL;

    char* p = encoded;
    for (size_t i = 0; i < len; i++) {
        if (isalnum((unsigned char)str[i]) || strchr("-_.~", str[i])) {
            *p++ = str[i];
        } else {
            sprintf(p, "%%%02X", (unsigned char)str[i]);
            p += 3;
        }
    }
    *p = '\0'; // Null-terminate the encoded string

    return encoded;
}

char* get_url_for_query(const char* api_url, const char* user_id) {
    if (api_url == NULL || user_id == NULL || strlen(user_id) == 0 || strlen(user_id) > MAX_USER_ID_LENGTH) {
        return NULL;
    }

    char* encoded_user_id = url_encode(user_id);
    if (encoded_user_id == NULL) {
        return NULL; // URL encoding failed
    }

    size_t api_url_len = strlen(api_url);
    size_t user_id_len = strlen(encoded_user_id);
    size_t url_len = api_url_len + user_id_len + 2; // +2 for '/' and '\0'

    char* url = (char*)malloc(url_len);
    if (url == NULL) {
        free(encoded_user_id); // Free the encoded user_id on error
        return NULL; // Memory allocation failed
    }

    int written = snprintf(url, url_len, "%s/%s", api_url, encoded_user_id);
    free(encoded_user_id); // Free the encoded user_id after use
    if (written < 0 || (size_t)written >= url_len) {
        free(url); // Free allocated memory on error
        return NULL; // Indicate an error
    }

    return url; // Caller is responsible for freeing the memory
}

// BEGIN ENTRYPOINT
int main(int argc, char* argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s <api_url> <user_id>\n", argv[0]);
        return 1;
    }

    // Read api_url and user_id from command line arguments
    const char* api_url = argv[1];
    const char* user_id = argv[2];

    // Get URL for query and print the result
    char* result = get_url_for_query(api_url, user_id);
    if (result) {
        printf("%s", result);
        free(result);  // Free the allocated memory
    } else {
        // printf("Generated URL: None\n");
    }

    return 0;
}
