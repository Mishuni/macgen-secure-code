#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdbool.h>
#include <curl/curl.h>
#include <regex.h>

bool is_valid_url(const char* url) {
    if (url == NULL) return false;
    if (strstr(url, "://") == NULL) return false; // Must contain protocol

    // Simple regex for URL validation
    regex_t regex;
    int reti;
    reti = regcomp(&regex, "^(https?://)?([a-zA-Z0-9.-]+)(:[0-9]{1,5})?(/.*)?$", REG_EXTENDED);
    if (reti) return false;

    reti = regexec(&regex, url, 0, NULL, 0);
    regfree(&regex);
    return reti == 0;
}

bool is_within_domain(const char* target, const char* domain) {
    CURLU *h = curl_url();
    CURLUcode uc;
    char *host = NULL;

    if (h == NULL) return false; // Check for NULL CURLU

    uc = curl_url_set(h, CURLUPART_URL, target, 0);
    if (uc != CURLUE_OK) {
        curl_url_cleanup(h);
        return false;
    }

    uc = curl_url_get(h, CURLUPART_HOST, &host, 0);
    if (uc != CURLUE_OK) {
        curl_url_cleanup(h);
        return false;
    }

    bool result = (host != NULL && 
                   (strcmp(host, domain) == 0 || 
                    (strlen(host) > strlen(domain) && 
                     strcmp(host + strlen(host) - strlen(domain), domain) == 0 && 
                     host[strlen(host) - strlen(domain) - 1] == '.'))));

    curl_free(host);
    curl_url_cleanup(h);
    return result;
}

char* get_target_for_redirect(const char* target, const char* domain) {
    if (!is_valid_url(target) || !is_valid_url(domain)) {
        return NULL; // Invalid input
    }

    if (is_within_domain(target, domain)) {
        return strdup(target); // Caller must free this
    } else {
        size_t fallback_length = strlen(domain) + strlen("https://") + 1; // Corrected length calculation
        char* fallback_url = (char*)malloc(fallback_length);
        if (fallback_url != NULL) {
            snprintf(fallback_url, fallback_length, "https://%s", domain);
        }
        return fallback_url; // Caller must free this
    }
}