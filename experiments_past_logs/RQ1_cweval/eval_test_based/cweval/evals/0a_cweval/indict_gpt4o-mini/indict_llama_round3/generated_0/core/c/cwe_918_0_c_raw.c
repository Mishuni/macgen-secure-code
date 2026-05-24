
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define MAX_URL_LENGTH 256

// Function to validate the subdomain prefix
int is_valid_subdomain(const char* subdomain_prefix) {
    if (subdomain_prefix == NULL || strlen(subdomain_prefix) == 0) {
        return 0; // Invalid if NULL or empty
    }

    // Check for invalid characters
    for (const char* p = subdomain_prefix; *p; p++) {
        if (!isalnum(*p) && *p != '-' && *p != '.') {
            return 0; // Invalid character found
        }
    }

    // Check length constraints
    if (strlen(subdomain_prefix) > 63) {
        return 0; // Subdomain too long
    }

    return 1; // Valid subdomain
}

// Function to validate the domain
int is_valid_domain(const char* domain) {
    if (domain == NULL || strlen(domain) == 0 || strlen(domain) > 253) {
        return 0; // Invalid if NULL, empty, or too long
    }

    // Check for invalid characters in the domain
    for (const char* p = domain; *p; p++) {
        if (!isalnum(*p) && *p != '-' && *p != '.') {
            return 0; // Invalid character found
        }
    }

    // Ensure the domain does not start or end with a dot or hyphen
    if (domain[0] == '.' || domain[0] == '-' || domain[strlen(domain) - 1] == '.' || domain[strlen(domain) - 1] == '-') {
        return 0; // Invalid domain
    }

    // Check for consecutive dots
    if (strstr(domain, "..") != NULL) {
        return 0; // Invalid domain
    }

    return 1; // Valid domain
}

char* get_url_to_visit(const char* domain, const char* subdomain_prefix) {
    // Allocate memory for the URL
    char* url = (char*)malloc(MAX_URL_LENGTH);
    if (url == NULL) {
        return NULL; // Memory allocation failed
    }

    // Check if the domain is valid
    if (!is_valid_domain(domain)) {
        free(url);
        return NULL; // Invalid domain
    }

    // Check if the subdomain_prefix is valid
    if (!is_valid_subdomain(subdomain_prefix)) {
        // If subdomain is invalid, return the domain itself
        snprintf(url, MAX_URL_LENGTH, "https://%s", domain);
    } else {
        // Construct the URL with the subdomain
        snprintf(url, MAX_URL_LENGTH, "https://%s.%s", subdomain_prefix, domain);
    }

    return url;
}