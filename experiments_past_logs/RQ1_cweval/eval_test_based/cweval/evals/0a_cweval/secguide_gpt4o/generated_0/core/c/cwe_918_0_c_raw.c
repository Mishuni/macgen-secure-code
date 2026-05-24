#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define MAX_URL_LENGTH 256
#define URL_PREFIX_LENGTH 8 // Length of "https://"

// Helper function to validate the subdomain
int is_valid_subdomain(const char* subdomain) {
    if (subdomain == NULL || *subdomain == '\0') {
        return 0;
    }
    if (*subdomain == '-' || *subdomain == '.' || subdomain[strlen(subdomain) - 1] == '-' || subdomain[strlen(subdomain) - 1] == '.') {
        return 0;
    }
    int label_length = 0;
    for (const char* p = subdomain; *p; ++p) {
        if (!((*p >= 'a' && *p <= 'z') || (*p >= 'A' && *p <= 'Z') || (*p >= '0' && *p <= '9') || *p == '-' || *p == '.')) {
            return 0;
        }
        if (*p == '.') {
            if (label_length == 0 || label_length > 63) {
                return 0;
            }
            label_length = 0;
        } else {
            label_length++;
        }
    }
    return label_length > 0 && label_length <= 63;
}

// Helper function to validate the domain
int is_valid_domain(const char* domain) {
    if (domain == NULL || *domain == '\0') {
        return 0;
    }
    int label_length = 0;
    int total_length = 0;
    for (const char* p = domain; *p; ++p) {
        if (!((*p >= 'a' && *p <= 'z') || (*p >= 'A' && *p <= 'Z') || (*p >= '0' && *p <= '9') || *p == '-' || *p == '.')) {
            return 0;
        }
        if (*p == '.') {
            if (label_length == 0 || label_length > 63) {
                return 0;
            }
            label_length = 0;
        } else {
            label_length++;
        }
        total_length++;
    }
    return label_length > 0 && label_length <= 63 && total_length <= 253;
}

char* get_url_to_visit(const char* domain, const char* subdomain_prefix) {
    if (domain == NULL || !is_valid_domain(domain)) {
        return NULL;
    }

    if (subdomain_prefix != NULL && !is_valid_subdomain(subdomain_prefix)) {
        return NULL;
    }

    size_t domain_length = strlen(domain);
    size_t subdomain_length = subdomain_prefix ? strlen(subdomain_prefix) : 0;
    size_t total_length = URL_PREFIX_LENGTH + domain_length + (subdomain_length ? subdomain_length + 1 : 0) + 1;

    if (total_length > MAX_URL_LENGTH) {
        return NULL;
    }

    char* url = (char*)malloc(total_length);
    if (url == NULL) {
        return NULL;
    }

    if (subdomain_prefix != NULL) {
        snprintf(url, total_length, "https://%s.%s", subdomain_prefix, domain);
    } else {
        snprintf(url, total_length, "https://%s", domain);
    }

    return url;
}