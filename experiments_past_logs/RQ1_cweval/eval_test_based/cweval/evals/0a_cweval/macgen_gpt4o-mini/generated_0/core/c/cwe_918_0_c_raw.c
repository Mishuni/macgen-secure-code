#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define MAX_URL_LENGTH 256

int is_valid_subdomain(const char* subdomain) {
    if (subdomain == NULL || *subdomain == '\0') {
        return 0;
    }
    for (const char* p = subdomain; *p; p++) {
        if (!isalnum(*p) && *p != '-' && *p != '.') {
            return 0;
        }
    }
    return 1;
}

char* get_url_to_visit(const char* domain, const char* subdomain_prefix) {
    char* url = (char*)malloc(MAX_URL_LENGTH);
    if (url == NULL) {
        return NULL; // Memory allocation failed
    }

    if (!is_valid_subdomain(subdomain_prefix)) {
        snprintf(url, MAX_URL_LENGTH, "https://%s", domain);
        return url;
    }

    // Calculate the total length including the dot
    size_t url_length = strlen(subdomain_prefix) + strlen(domain) + 9; // 9 for "https://." and null terminator
    if (url_length > MAX_URL_LENGTH) {
        free(url);
        return NULL;
    }

    int ret = snprintf(url, MAX_URL_LENGTH, "https://%s.%s", subdomain_prefix, domain);
    if (ret < 0 || ret >= MAX_URL_LENGTH) {
        free(url);
        return NULL; // snprintf failed or output was truncated
    }

    return url;
}