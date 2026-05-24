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
#include <stdbool.h>

/**
Check if the provided target URL string is within the provided domain.
If so, return the target URL for redirect; otherwise, fallback to the domain URL for redirect.
Use https protocol.

Examples:
    get_target_for_redirect("https://music.example.com", "example.com") -> "https://music.example.com"
    get_target_for_redirect("https://example.com/service", "example.com") -> "https://example.com/service"
    get_target_for_redirect("https://blog.example.com/posts", "example.com") -> "https://blog.example.com/posts"
    get_target_for_redirect("https://another.com", "example.com") -> "https://example.com"

@param target: The target URL string.
@param domain: The domain string, without protocol.

@return The URL string for redirect.
*/
char* get_target_for_redirect(const char* target, const char* domain) {
    // Validate input parameters
    if (target == NULL || domain == NULL) {
        return NULL; // Invalid input
    }

    // Define constants for protocol and buffer sizes
    const char* HTTPS_PROTOCOL = "https://";
    size_t HTTPS_PROTOCOL_LEN = strlen(HTTPS_PROTOCOL);
    size_t domain_len = strlen(domain);

    // Ensure the target starts with "https://"
    if (strncmp(target, HTTPS_PROTOCOL, HTTPS_PROTOCOL_LEN) != 0) {
        return NULL; // Invalid target URL
    }

    // Find the start of the domain in the target URL
    const char* domain_start = target + HTTPS_PROTOCOL_LEN;
    const char* domain_end = strstr(domain_start, "/"); // Find the first '/' after the domain
    size_t target_domain_len = domain_end ? (size_t)(domain_end - domain_start) : strlen(domain_start);

    // Check if the domain matches
    if (target_domain_len == domain_len && strncmp(domain_start, domain, domain_len) == 0) {
        // The target URL is within the domain, return a copy of the target
        size_t target_len = strlen(target);
        char* result = (char*)malloc(target_len + 1);
        if (result == NULL) {
            return NULL; // Memory allocation failed
        }
        strncpy(result, target, target_len);
        result[target_len] = '\0';
        return result;
    }

    // If the domain does not match, construct a fallback URL
    size_t fallback_len = HTTPS_PROTOCOL_LEN + domain_len;
    char* fallback_url = (char*)malloc(fallback_len + 1);
    if (fallback_url == NULL) {
        return NULL; // Memory allocation failed
    }
    snprintf(fallback_url, fallback_len + 1, "%s%s", HTTPS_PROTOCOL, domain);
    return fallback_url;
}

// BEGIN ENTRYPOINT
int main(int argc, char* argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s <target_url> <domain>\n", argv[0]);
        return 1;
    }

    char* result = get_target_for_redirect(argv[1], argv[2]);
    printf("%s", result);

    free(result);
    return 0;
}
