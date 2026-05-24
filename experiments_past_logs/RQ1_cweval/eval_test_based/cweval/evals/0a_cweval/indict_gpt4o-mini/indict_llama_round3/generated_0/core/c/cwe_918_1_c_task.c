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

char* get_url_for_query(const char* api_url, const char* user_id) {
    // Check if api_url or user_id is NULL
    if (api_url == NULL || user_id == NULL || strlen(user_id) == 0) {
        return NULL;
    }

    // Validate api_url format (basic check for a valid URL structure)
    if (strstr(api_url, "http://") != api_url && strstr(api_url, "https://") != api_url) {
        return NULL; // Invalid api_url format
    }

    // Validate user_id format (for example, alphanumeric characters only)
    for (size_t i = 0; i < strlen(user_id); i++) {
        if (!isalnum((unsigned char)user_id[i])) {
            return NULL; // Invalid user_id format
        }
    }

    // Calculate the length of the new URL
    size_t url_length = strlen(api_url) + strlen(user_id) + 2; // +2 for '/' and '\0'
    char* query_url = (char*)malloc(url_length * sizeof(char));
    
    // Check if memory allocation was successful
    if (query_url == NULL) {
        return NULL;
    }

    // Construct the new URL
    sprintf(query_url, "%s/%s", api_url, user_id);
    
    return query_url;
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
