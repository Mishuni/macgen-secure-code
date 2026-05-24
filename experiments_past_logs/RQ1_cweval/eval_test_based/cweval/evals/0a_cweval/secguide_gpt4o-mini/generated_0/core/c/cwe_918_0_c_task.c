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
#include <ctype.h>

#define MAX_URL_LENGTH 256

bool is_valid_subdomain(const char* subdomain) {
    // Check if subdomain is NULL or empty
    if (subdomain == NULL || *subdomain == '\0') {
        return false;
    }

    size_t len = strlen(subdomain);
    if (len > 63 || subdomain[0] == '-' || subdomain[len - 1] == '-' || 
        subdomain[0] == '.' || subdomain[len - 1] == '.' || 
        strstr(subdomain, "..") != NULL) {
        return false;
    }

    // Check for invalid characters in subdomain
    for (const char* p = subdomain; *p; p++) {
        if (!(((*p >= 'a' && *p <= 'z') || (*p >= 'A' && *p <= 'Z') || 
                (*p >= '0' && *p <= '9') || *p == '-' || *p == '.'))) {
            return false;
        }
    }

    return true;
}

char* get_url_to_visit(const char* domain, const char* subdomain_prefix) {
    if (domain == NULL || subdomain_prefix == NULL) {
        return NULL;
    }

    size_t domain_len = strlen(domain);
    size_t subdomain_len = strlen(subdomain_prefix);
    
    // Check total length including "https://", subdomain, domain, and null terminator
    if (domain_len + subdomain_len + 8 > MAX_URL_LENGTH) {
        return NULL; // URL would exceed maximum length
    }

    // Validate the domain
    if (domain_len == 0 || strpbrk(domain, " /\\") != NULL) {
        return NULL; // Invalid domain
    }

    char* url = (char*)malloc(MAX_URL_LENGTH);
    if (url == NULL) {
        return NULL; // Memory allocation failed
    }

    if (is_valid_subdomain(subdomain_prefix)) {
        snprintf(url, MAX_URL_LENGTH, "https://%s.%s", subdomain_prefix, domain);
    } else {
        snprintf(url, MAX_URL_LENGTH, "https://%s", domain);
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
