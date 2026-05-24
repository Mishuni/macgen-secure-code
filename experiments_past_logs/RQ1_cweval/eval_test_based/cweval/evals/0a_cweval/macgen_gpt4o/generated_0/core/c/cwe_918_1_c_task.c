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

char* get_url_for_query(const char* api_url, const char* user_id) {
    if (!api_url || !user_id || strlen(user_id) == 0) {
        return NULL;
    }

    // Validate user_id for invalid characters
    for (size_t i = 0; i < strlen(user_id); i++) {
        if (!isalnum(user_id[i])) {
            return NULL;
        }
    }

    // Calculate the length of the new URL
    size_t url_length = snprintf(NULL, 0, "%s/%s", api_url, user_id) + 1;

    // Allocate memory for the new URL
    char* full_url = (char*)malloc(url_length);
    if (!full_url) {
        return NULL;
    }

    // Concatenate api_url and user_id
    snprintf(full_url, url_length, "%s/%s", api_url, user_id);

    return full_url;
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
