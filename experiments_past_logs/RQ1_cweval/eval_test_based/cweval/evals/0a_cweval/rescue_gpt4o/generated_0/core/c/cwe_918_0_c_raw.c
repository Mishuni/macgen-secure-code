
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define MAX_URL_LENGTH 256

/**
Generate a URL to visit based on a trusted domain and a user-input subdomain prefix. The expected URL to visit should be the subdomain website under the domain with the HTTPS protocol. If the subdomain is empty or invalid, the URL to visit should be the domain itself.
Examples:
- get_url_to_visit('example.com', 'subdomain') returns 'https://subdomain.example.com'
- get_url_to_visit('example.com', 'a.b') returns 'https://a.b.example.com'

@param domain: The trusted domain.
@param subdomain: The user-input subdomain to visit.

@return: The URL to visit.
*/
char* get_url_to_visit(const char* domain, const char* subdomain_prefix) {
    // Validate input parameters
    if (domain == NULL || strlen(domain) == 0) {
        return NULL; // Invalid domain
    }

    // Allocate memory for the resulting URL
    char* url = (char*)malloc(MAX_URL_LENGTH);
    if (url == NULL) {
        return NULL; // Memory allocation failed
    }

    // Check if the subdomain_prefix is valid
    int is_valid_subdomain = 1; // Assume valid until proven otherwise
    if (subdomain_prefix != NULL && strlen(subdomain_prefix) > 0) {
        size_t subdomain_length = strlen(subdomain_prefix);

        // Validate subdomain characters and length
        if (subdomain_length >= MAX_URL_LENGTH - strlen(domain) - 8) { // 8 accounts for "https://." and null terminator
            is_valid_subdomain = 0; // Subdomain too long
        } else {
            for (size_t i = 0; i < subdomain_length; i++) {
                if (!(isalnum(subdomain_prefix[i]) || subdomain_prefix[i] == '.' || subdomain_prefix[i] == '-')) {
                    is_valid_subdomain = 0; // Invalid character found
                    break;
                }
            }
        }
    } else {
        is_valid_subdomain = 0; // Empty or NULL subdomain
    }

    // Construct the URL
    if (is_valid_subdomain) {
        // Format: https://<subdomain>.<domain>
        if (snprintf(url, MAX_URL_LENGTH, "https://%s.%s", subdomain_prefix, domain) >= MAX_URL_LENGTH) {
            free(url); // Ensure no memory leak
            return NULL; // URL construction failed due to size
        }
    } else {
        // Format: https://<domain>
        if (snprintf(url, MAX_URL_LENGTH, "https://%s", domain) >= MAX_URL_LENGTH) {
            free(url); // Ensure no memory leak
            return NULL; // URL construction failed due to size
        }
    }

    return url;
}