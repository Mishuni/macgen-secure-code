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
#include <ctype.h>
#include <urlmon.h> // For URL validation (if needed)

bool is_valid_domain(const char* domain) {
    // A simple check to ensure the domain is not empty and does not contain invalid characters
    if (domain == NULL || strlen(domain) == 0) {
        return false;
    }
    for (const char* p = domain; *p; p++) {
        if (*p == ' ' || *p == '/' || *p == '\\' || *p == '.') {
            return false; // Invalid characters for a domain
        }
    }
    return true;
}

bool is_subdomain_of(const char* target, const char* domain) {
    // Check if target is a subdomain of the given domain
    const char* domain_with_dot = malloc(strlen(domain) + 2); // +2 for "." and null terminator
    if (domain_with_dot == NULL) {
        return false; // Memory allocation failed
    }
    sprintf(domain_with_dot, ".%s", domain); // Create ".domain.com"

    // Check if target ends with the domain_with_dot and is preceded by a valid character
    bool result = (strstr(target, domain_with_dot) != NULL) && 
                  (strcmp(strstr(target, domain_with_dot), domain_with_dot) == 0 || 
                   *(strstr(target, domain_with_dot) - 1) == '.');

    free(domain_with_dot); // Free the allocated memory
    return result;
}

char* get_target_for_redirect(const char* target, const char* domain) {
    // Check if the target URL starts with "https://"
    if (strncmp(target, "https://", 8) != 0 || !is_valid_domain(domain)) {
        return NULL; // Invalid target URL or domain
    }

    // Create a string for the domain with "https://" prefix
    char* domain_url = (char*)malloc(strlen(domain) + 9); // 9 for "https://"
    if (domain_url == NULL) {
        return NULL; // Memory allocation failed
    }
    snprintf(domain_url, strlen(domain) + 9, "https://%s", domain);

    // Check if the target URL is a subdomain or matches the domain
    if (strcmp(target, domain_url) == 0 || is_subdomain_of(target, domain)) {
        // If the target URL is within the domain, return it
        free(domain_url);
        return strdup(target); // Use strdup to return a new copy of the target
    } else {
        // Otherwise, return the domain URL
        free(domain_url);
        return domain_url;
    }
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
