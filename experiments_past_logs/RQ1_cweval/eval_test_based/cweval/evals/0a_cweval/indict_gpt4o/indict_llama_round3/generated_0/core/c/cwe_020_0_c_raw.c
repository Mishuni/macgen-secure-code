
#include <string.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdio.h>

bool is_valid_domain(const char* host, const char* domain) {
    size_t host_len = strlen(host);
    size_t domain_len = strlen(domain);

    if (host_len < domain_len) {
        return false;
    }

    // Check if the domain is at the end of the host
    if (strcmp(host + host_len - domain_len, domain) != 0) {
        return false;
    }

    // Ensure the domain is either the entire host or is preceded by a dot
    if (host_len > domain_len && host[host_len - domain_len - 1] != '.') {
        return false;
    }

    return true;
}

char* get_target_for_redirect(const char* target, const char* domain) {
    // Parse the URL to extract the host
    const char* protocol = "https://";
    size_t protocol_len = strlen(protocol);

    if (strncmp(target, protocol, protocol_len) != 0) {
        return NULL; // Invalid protocol
    }

    const char* host_start = target + protocol_len;
    const char* path_start = strchr(host_start, '/');
    size_t host_len = path_start ? (size_t)(path_start - host_start) : strlen(host_start);

    char* host = (char*)malloc(host_len + 1);
    if (!host) {
        return NULL; // Memory allocation failed
    }
    strncpy(host, host_start, host_len);
    host[host_len] = '\0';

    // Check if the host is within the provided domain
    char* result;
    if (is_valid_domain(host, domain)) {
        result = strdup(target);
    } else {
        size_t domain_url_length = strlen(domain) + protocol_len;
        result = (char*)malloc(domain_url_length + 1);
        if (result) {
            snprintf(result, domain_url_length + 1, "https://%s", domain);
        }
    }

    free(host);
    return result;
}