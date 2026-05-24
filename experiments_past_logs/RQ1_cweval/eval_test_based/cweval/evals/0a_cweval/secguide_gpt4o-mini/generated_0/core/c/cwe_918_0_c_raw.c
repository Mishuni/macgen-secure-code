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