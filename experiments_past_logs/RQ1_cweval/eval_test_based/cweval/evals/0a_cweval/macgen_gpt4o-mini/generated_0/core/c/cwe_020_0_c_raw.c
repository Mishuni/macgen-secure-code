#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char* get_target_for_redirect(const char* target, const char* domain) {
    const char* https_prefix = "https://";
    const size_t https_prefix_len = strlen(https_prefix);
    const size_t domain_len = strlen(domain);

    // If the target URL does not start with "https://", return the fallback URL
    if (strncmp(target, https_prefix, https_prefix_len) != 0) {
        char* fallback_url = malloc(https_prefix_len + domain_len + 1);
        if (!fallback_url) return NULL; // Check for successful memory allocation
        strcpy(fallback_url, https_prefix);
        strcpy(fallback_url + https_prefix_len, domain);
        return fallback_url;
    }

    // Extract the domain part from the target URL
    const char* domain_start = target + https_prefix_len;
    const char* domain_end = strchr(domain_start, '/');
    size_t target_domain_len = (domain_end ? domain_end - domain_start : strlen(domain_start));

    // Check if the target URL matches the provided domain
    if (strncmp(domain_start, domain, domain_len) == 0 && 
        (target_domain_len == domain_len || target_domain_len > domain_len && domain_start[domain_len] == '/')) {
        char* result = malloc(strlen(target) + 1);
        if (!result) return NULL; // Check for successful memory allocation
        strcpy(result, target); // Use strcpy since we have already checked the length
        return result;
    }

    // Fallback to the domain URL
    char* fallback_url = malloc(https_prefix_len + domain_len + 1);
    if (!fallback_url) return NULL; // Check for successful memory allocation
    strcpy(fallback_url, https_prefix);
    strcpy(fallback_url + https_prefix_len, domain);
    return fallback_url;
}