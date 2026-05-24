
// SPDX-License-Identifier: GPL-3.0-or-later

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <ctype.h>

bool is_subdomain(const char* target, const char* domain) {
    const char* domain_with_protocol = "https://";
    const char* domain_start = strstr(target, domain_with_protocol);
    
    if (domain_start) {
        domain_start += strlen(domain_with_protocol);
    } else {
        domain_start = strstr(target, domain);
    }

    if (domain_start) {
        const char* end_of_domain = domain_start + strlen(domain);
        if ((*end_of_domain == '/' || *end_of_domain == '\0') && 
            (domain_start == target || *(domain_start - 1) == '.')) {
            return true;
        }
    }
    return false;
}

char* get_target_for_redirect(const char* target, const char* domain) {
    if (target == NULL || domain == NULL || strlen(domain) == 0) {
        return NULL; // Handle null or empty domain
    }

    if (is_subdomain(target, domain)) {
        return strdup(target); // Return a copy of the target URL
    } else {
        char* fallback_url = malloc(strlen("https://") + strlen(domain) + 1);
        if (fallback_url == NULL) {
            return NULL; // Handle memory allocation failure
        }
        sprintf(fallback_url, "https://%s", domain);
        return fallback_url; // Return the fallback URL
    }
}