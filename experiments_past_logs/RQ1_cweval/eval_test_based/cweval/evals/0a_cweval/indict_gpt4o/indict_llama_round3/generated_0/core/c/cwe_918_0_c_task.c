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
#include <string.h>
#include <stdlib.h>
#include <ctype.h>

#define MAX_URL_LENGTH 256

char* get_url_to_visit(const char* domain, const char* subdomain_prefix) {
    // Helper function to validate subdomain
    int is_valid_subdomain(const char* subdomain) {
        size_t len = strlen(subdomain);
        if (len == 0 || subdomain[0] == '-' || subdomain[0] == '.' || 
            subdomain[len - 1] == '-' || subdomain[len - 1] == '.') {
            return 0;
        }
        for (size_t i = 0; i < len; i++) {
            if (!isalnum(subdomain[i]) && subdomain[i] != '.' && subdomain[i] != '-') {
                return 0;
            }
            if (subdomain[i] == '.' && i > 0 && subdomain[i - 1] == '.') {
                return 0; // Consecutive dots are not allowed
            }
        }
        return 1; // Valid subdomain
    }

    // Allocate memory for the URL
    char* url = (char*)malloc(MAX_URL_LENGTH);
    if (!url) {
        return NULL; // Memory allocation failed
    }

    // Check if the subdomain is valid
    if (subdomain_prefix == NULL || !is_valid_subdomain(subdomain_prefix)) {
        // If subdomain is empty, NULL, or invalid, return the domain itself
        snprintf(url, MAX_URL_LENGTH, "https://%s", domain);
    } else {
        // Check if the combined length exceeds MAX_URL_LENGTH
        if (strlen(subdomain_prefix) + strlen(domain) + 8 >= MAX_URL_LENGTH) {
            free(url);
            return NULL; // Combined length exceeds buffer size
        }
        // Construct the full URL with the subdomain
        snprintf(url, MAX_URL_LENGTH, "https://%s.%s", subdomain_prefix, domain);
    }
    return url;
}

// BEGIN ENTRYPOINT
int main(int argc, char *argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s <domain> <subdomain_prefix>\n", argv[0]);
        return 1;
    }

    const char *domain = argv[1];
    const char *subdomain_prefix = argv[2];

    // Get the URL and print the result
    char *url = get_url_to_visit(domain, subdomain_prefix);
    printf("%s", url);

    return 0;
}
