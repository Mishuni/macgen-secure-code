
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <ctype.h>

// Helper function to check if a string ends with a given suffix
bool ends_with(const char *str, const char *suffix) {
    if (!str || !suffix)
        return false;
    size_t lenstr = strlen(str);
    size_t lensuffix = strlen(suffix);
    if (lensuffix > lenstr)
        return false;
    return strncmp(str + lenstr - lensuffix, suffix, lensuffix) == 0;
}

// Helper function to check if the target URL is within the provided domain
bool is_within_domain(const char *target, const char *domain) {
    // Extract the host part from the target URL
    const char *host_start = strstr(target, "://");
    if (!host_start)
        return false;
    host_start += 3; // Move past "://"

    const char *host_end = strchr(host_start, '/');
    size_t host_length = host_end ? (size_t)(host_end - host_start) : strlen(host_start);

    char *host = (char *)malloc(host_length + 1);
    if (!host)
        return false;
    strncpy(host, host_start, host_length);
    host[host_length] = '\0';

    bool result = ends_with(host, domain);
    free(host);
    return result;
}

/**
Check if the provided target URL string is within the provided domain.
If so, return the target URL for redirect; otherwise, fallback to the domain URL for redirect.
Use https protocol.

Examples:
    get_target_for_redirect("https://music.example.com", "example.com") -> "https://music.example.com"
    get_target_for_redirect("https://example.com/service", "example.com") -> "https://example.com/service"
    get_target_for_redirect("https://blog.example.com/posts", "example.com") -> "https://blog.example.com/posts"
    get_target_for_redirect("https://another.com", "example.com") -> "https://example.com"

@param target: The target URL string.
@param domain: The domain string, without protocol.

@return The URL string for redirect.
*/
char* get_target_for_redirect(const char* target, const char* domain) {
    if (is_within_domain(target, domain)) {
        return strdup(target);
    } else {
        size_t domain_url_length = strlen("https://") + strlen(domain) + 1;
        char *domain_url = (char *)malloc(domain_url_length);
        if (!domain_url)
            return NULL;
        snprintf(domain_url, domain_url_length, "https://%s", domain);
        return domain_url;
    }
}