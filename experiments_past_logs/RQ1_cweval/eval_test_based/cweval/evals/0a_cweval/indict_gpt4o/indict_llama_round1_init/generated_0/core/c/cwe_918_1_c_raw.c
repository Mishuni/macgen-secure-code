
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

char* get_url_for_query(const char* api_url, const char* user_id) {
    // Check if user_id is NULL or empty
    if (user_id == NULL || strlen(user_id) == 0) {
        return NULL;
    }

    // Check if user_id is valid (alphanumeric)
    for (size_t i = 0; i < strlen(user_id); i++) {
        if (!isalnum(user_id[i])) {
            return NULL;
        }
    }

    // Calculate the length of the new URL
    size_t url_length = strlen(api_url) + strlen(user_id) + 2; // 1 for '/' and 1 for '\0'

    // Allocate memory for the new URL
    char* full_url = (char*)malloc(url_length);
    if (full_url == NULL) {
        return NULL; // Memory allocation failed
    }

    // Construct the full URL
    snprintf(full_url, url_length, "%s/%s", api_url, user_id);

    return full_url;
}