#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

bool starts_with(const char* str, const char* prefix) {
    return strncmp(str, prefix, strlen(prefix)) == 0;
}

bool ends_with(const char* str, const char* suffix) {
    if (!str || !suffix) return false;
    size_t str_len = strlen(str);
    size_t suffix_len = strlen(suffix);
    if (suffix_len > str_len) return false;
    return strncmp(str + str_len - suffix_len, suffix, suffix_len) == 0;
}

char* extract_domain(const char* url) {
    const char* start = strstr(url, "://");
    if (!start) return NULL;
    start += 3; // Skip "://"
    const char* end = strchr(start, '/');
    size_t len = end ? (size_t)(end - start) : strlen(start);
    char* domain = (char*)malloc(len + 1);
    if (!domain) return NULL;
    strncpy(domain, start, len);
    domain[len] = '\0';
    return domain;
}

char* get_target_for_redirect(const char* target, const char* domain) {
    if (!starts_with(target, "https://")) {
        size_t domain_len = strlen(domain);
        char* fallback_url = (char*)malloc(domain_len + 9); // "https://" + domain + '\0'
        if (!fallback_url) return NULL;
        snprintf(fallback_url, domain_len + 9, "https://%s", domain);
        return fallback_url;
    }

    char* target_domain = extract_domain(target);
    if (!target_domain) {
        size_t domain_len = strlen(domain);
        char* fallback_url = (char*)malloc(domain_len + 9); // "https://" + domain + '\0'
        if (!fallback_url) return NULL;
        snprintf(fallback_url, domain_len + 9, "https://%s", domain);
        return fallback_url;
    }

    char* result;
    if (ends_with(target_domain, domain)) {
        result = strdup(target);
    } else {
        size_t domain_len = strlen(domain);
        result = (char*)malloc(domain_len + 9); // "https://" + domain + '\0'
        if (result) {
            snprintf(result, domain_len + 9, "https://%s", domain);
        }
    }

    free(target_domain);
    return result;
}