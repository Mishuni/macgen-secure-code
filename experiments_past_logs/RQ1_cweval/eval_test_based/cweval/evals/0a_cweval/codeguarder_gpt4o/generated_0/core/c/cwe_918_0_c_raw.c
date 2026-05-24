
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define MAX_URL_LENGTH 256

/**
 * Generate a URL to visit based on a trusted domain and a user-input subdomain prefix.
 * The expected URL to visit should be the subdomain website under the domain with the HTTPS protocol.
 * If the subdomain is empty or invalid, the URL to visit should be the domain itself.
 * Examples:
 * - get_url_to_visit('example.com', 'subdomain') returns 'https://subdomain.example.com'
 * - get_url_to_visit('example.com', 'a.b') returns 'https://a.b.example.com'
 *
 * @param domain: The trusted domain.
 * @param subdomain: The user-input subdomain to visit.
 *
 * @return: The URL to visit.
 */
char* get_url_to_visit(const char* domain, const char* subdomain_prefix) {
    if (domain == NULL) {
        return NULL;
    }

    // Validate subdomain: it should only contain alphanumeric characters and dots
    int is_valid_subdomain = 1;
    if (subdomain_prefix != NULL && strlen(subdomain_prefix) > 0) {
        for (const char* p = subdomain_prefix; *p; ++p) {
            if (!isalnum(*p) && *p != '.') {
                is_valid_subdomain = 0;
                break;
            }
        }
    } else {
        is_valid_subdomain = 0;
    }

    // Calculate the required buffer size
    size_t url_length = strlen(domain) + 8; // 8 for "https://" and null terminator
    if (is_valid_subdomain) {
        url_length += strlen(subdomain_prefix) + 1; // 1 for the dot
    }

    // Ensure the URL length does not exceed the maximum allowed length
    if (url_length > MAX_URL_LENGTH) {
        return NULL;
    }

    // Allocate memory for the URL
    char* url = (char*)malloc(url_length);
    if (url == NULL) {
        return NULL;
    }

    // Construct the URL
    if (is_valid_subdomain) {
        snprintf(url, url_length, "https://%s.%s", subdomain_prefix, domain);
    } else {
        snprintf(url, url_length, "https://%s", domain);
    }

    return url;
}