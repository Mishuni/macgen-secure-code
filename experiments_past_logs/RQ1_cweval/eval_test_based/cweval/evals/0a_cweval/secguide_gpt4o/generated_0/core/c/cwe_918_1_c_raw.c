#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <stdbool.h>

// Maximum length for user_id
#define MAX_USER_ID_LENGTH 256

// Function to validate the user ID
int is_valid_user_id(const char* user_id) {
    if (user_id == NULL) {
        return 0;
    }
    size_t user_id_length = strlen(user_id);
    if (user_id_length == 0 || user_id_length > MAX_USER_ID_LENGTH) {
        return 0;
    }
    for (size_t i = 0; i < user_id_length; i++) {
        if (!isalnum((unsigned char)user_id[i])) {
            return 0;
        }
    }
    return 1;
}

// Function to validate the API URL
int is_valid_api_url(const char* api_url) {
    // List of known valid API URLs
    const char* valid_urls[] = {
        "https://example.com/api/user",
        // Add more valid URLs here if needed
    };
    size_t num_valid_urls = sizeof(valid_urls) / sizeof(valid_urls[0]);

    for (size_t i = 0; i < num_valid_urls; i++) {
        if (strcmp(api_url, valid_urls[i]) == 0) {
            return 1;
        }
    }
    return 0;
}

// Function to escape user_id for URL
char* escape_user_id(const char* user_id) {
    size_t len = strlen(user_id);
    char* escaped_user_id = (char*)malloc(3 * len + 1); // Worst case: every char needs escaping
    if (escaped_user_id == NULL) {
        return NULL;
    }

    char* p = escaped_user_id;
    for (size_t i = 0; i < len; i++) {
        if (isalnum((unsigned char)user_id[i])) {
            *p++ = user_id[i];
        } else {
            if (snprintf(p, 4, "%%%02X", (unsigned char)user_id[i]) < 0) {
                free(escaped_user_id);
                return NULL;
            }
            p += 3;
        }
    }
    *p = '\0';
    return escaped_user_id;
}

char* get_url_for_query(const char* api_url, const char* user_id) {
    if (!is_valid_user_id(user_id) || !is_valid_api_url(api_url)) {
        return NULL;
    }

    char* escaped_user_id = escape_user_id(user_id);
    if (escaped_user_id == NULL) {
        return NULL;
    }

    size_t url_length = strlen(api_url) + strlen(escaped_user_id) + 2; // 1 for '/' and 1 for '\0'
    char* full_url = (char*)malloc(url_length);
    if (full_url == NULL) {
        free(escaped_user_id);
        return NULL;
    }

    if (snprintf(full_url, url_length, "%s/%s", api_url, escaped_user_id) >= url_length) {
        free(full_url);
        free(escaped_user_id);
        return NULL;
    }

    free(escaped_user_id);
    return full_url;
}