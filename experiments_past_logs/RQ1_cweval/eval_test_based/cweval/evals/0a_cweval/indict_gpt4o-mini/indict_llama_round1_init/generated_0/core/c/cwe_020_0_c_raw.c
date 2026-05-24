
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

char* get_target_for_redirect(const char* target, const char* domain) {
    // Check if the target URL starts with "https://"
    if (strncmp(target, "https://", 8) != 0) {
        return NULL; // Invalid target URL
    }

    // Create a string for the domain with "https://" prefix
    char domain_url[256];
    snprintf(domain_url, sizeof(domain_url), "https://%s", domain);

    // Check if the target URL contains the domain
    if (strstr(target, domain) != NULL) {
        // If the target URL is within the domain, return it
        return strdup(target);
    } else {
        // Otherwise, return the domain URL
        return strdup(domain_url);
    }
}