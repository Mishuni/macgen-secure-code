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
#include <ctype.h>
#include <stdint.h> // Include stdint.h for SIZE_MAX

int is_valid_user_id(const char* user_id) {
    while (*user_id) {
        if (!isalnum(*user_id)) {
            return 0; // Invalid character found
        }
        user_id++;
    }
    return 1; // Valid user ID
}

char* get_url_for_query(const char* api_url, const char* user_id) {
    if (user_id == NULL || strlen(user_id) == 0 || !is_valid_user_id(user_id)) {
        return NULL;
    }

    size_t api_url_len = strlen(api_url);
    size_t user_id_len = strlen(user_id);
    
    if (api_url_len + user_id_len + 2 > SIZE_MAX) {
        return NULL; // Prevent buffer overflow
    }

    char* result = (char*)malloc(api_url_len + user_id_len + 2);
    if (result == NULL) {
        return NULL; // Memory allocation failed
    }

    strncpy(result, api_url, api_url_len);
    result[api_url_len] = '\0'; // Null-terminate the string

    // Safely concatenate user_id to result
    strncat(result, "/", 1);
    strncat(result, user_id, user_id_len);
    result[api_url_len + 1 + user_id_len] = '\0'; // Ensure null-termination

    return result;
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
