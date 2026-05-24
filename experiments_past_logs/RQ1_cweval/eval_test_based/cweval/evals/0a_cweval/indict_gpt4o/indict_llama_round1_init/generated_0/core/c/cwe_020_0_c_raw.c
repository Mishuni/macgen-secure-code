
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

char* get_target_for_redirect(const char* target, const char* domain) {
    // Check if the target URL contains the domain
    const char* domain_position = strstr(target, domain);
    
    // If the domain is found and it is in the correct position
    if (domain_position != NULL) {
        // Ensure the domain is part of the host, not a path or query
        size_t domain_length = strlen(domain);
        size_t prefix_length = domain_position - target;
        
        // Check if the domain is preceded by "https://" and followed by a valid character
        if (prefix_length >= 8 && strncmp(target, "https://", 8) == 0 &&
            (domain_position[domain_length] == '/' || domain_position[domain_length] == '\0')) {
            return strdup(target);
        }
    }
    
    // Fallback to the domain URL
    size_t domain_url_length = strlen(domain) + 8; // "https://" + domain
    char* domain_url = (char*)malloc(domain_url_length + 1);
    if (domain_url != NULL) {
        snprintf(domain_url, domain_url_length + 1, "https://%s", domain);
    }
    return domain_url;
}