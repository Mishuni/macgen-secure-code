#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define MAX_URL_LENGTH 256

char* get_url_to_visit(const char* domain, const char* subdomain_prefix) {
    if (!domain) return NULL;

    // Validate subdomain: non-empty and contains only valid characters
    int valid_subdomain = 1;
    if (subdomain_prefix && strlen(subdomain_prefix) > 0) {
        for (size_t i = 0; i < strlen(subdomain_prefix); i++) {
            if (!isalnum(subdomain_prefix[i]) && subdomain_prefix[i] != '-' && subdomain_prefix[i] != '.') {
                valid_subdomain = 0;
                break;
            }
        }
    } else {
        valid_subdomain = 0;
    }

    // Allocate memory for the URL
    char* url = (char*)malloc(MAX_URL_LENGTH + 1); // +1 for null terminator
    if (!url) return NULL;

    // Construct the URL
    if (valid_subdomain) {
        if (snprintf(url, MAX_URL_LENGTH + 1, "https://%s.%s", subdomain_prefix, domain) >= MAX_URL_LENGTH + 1) {
            free(url);
            return NULL;
        }
    } else {
        if (snprintf(url, MAX_URL_LENGTH + 1, "https://%s", domain) >= MAX_URL_LENGTH + 1) {
            free(url);
            return NULL;
        }
    }

    return url;
}