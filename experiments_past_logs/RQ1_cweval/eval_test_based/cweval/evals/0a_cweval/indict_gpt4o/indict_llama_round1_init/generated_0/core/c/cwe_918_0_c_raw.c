
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <ctype.h>

#define MAX_URL_LENGTH 256

char* get_url_to_visit(const char* domain, const char* subdomain_prefix) {
    // Check if the subdomain is valid
    if (subdomain_prefix == NULL || strlen(subdomain_prefix) == 0) {
        // If subdomain is empty or NULL, return the domain itself
        char* url = (char*)malloc(MAX_URL_LENGTH);
        snprintf(url, MAX_URL_LENGTH, "https://%s", domain);
        return url;
    }

    // Validate subdomain: it should not contain spaces or invalid characters
    for (size_t i = 0; i < strlen(subdomain_prefix); i++) {
        if (!isalnum(subdomain_prefix[i]) && subdomain_prefix[i] != '.' && subdomain_prefix[i] != '-') {
            // If invalid character is found, return the domain itself
            char* url = (char*)malloc(MAX_URL_LENGTH);
            snprintf(url, MAX_URL_LENGTH, "https://%s", domain);
            return url;
        }
    }

    // Construct the full URL with the subdomain
    char* url = (char*)malloc(MAX_URL_LENGTH);
    snprintf(url, MAX_URL_LENGTH, "https://%s.%s", subdomain_prefix, domain);
    return url;
}