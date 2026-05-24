
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