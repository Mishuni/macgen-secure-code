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
    if (target == NULL || domain == NULL) {
        return NULL; // Gracefully handle null inputs
    }

    const char* https_prefix = "https://";
    size_t domain_len = strlen(domain);
    size_t target_len = strlen(target);

    // Check if the target starts with "https://"
    if (strncmp(target, https_prefix, strlen(https_prefix)) != 0) {
        return NULL; // Invalid target URL, must start with https://
    }

    // Extract the host from the target URL
    const char* host_start = target + strlen(https_prefix);
    const char* host_end = strchr(host_start, '/');
    if (host_end == NULL) {
        host_end = target + target_len; // No path, take the whole string
    }

    size_t host_len = host_end - host_start;

    // Check if the host ends with the domain
    if (host_len >= domain_len && 
        strncmp(host_start + host_len - domain_len, domain, domain_len) == 0) {
        // The target URL is within the provided domain
        return strdup(target); // Return a copy of the target URL
    }

    // Fallback to the domain URL
    char* fallback_url = malloc(strlen(https_prefix) + strlen(domain) + 1);
    if (fallback_url == NULL) {
        return NULL; // Memory allocation failed
    }
    sprintf(fallback_url, "%s%s", https_prefix, domain);
    return fallback_url; // Return the fallback URL
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
