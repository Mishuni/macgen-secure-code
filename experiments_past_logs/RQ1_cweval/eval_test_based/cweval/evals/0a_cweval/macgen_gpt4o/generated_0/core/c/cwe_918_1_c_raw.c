#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

char* get_url_for_query(const char* api_url, const char* user_id) {
    if (!api_url || !user_id || strlen(user_id) == 0) {
        return NULL;
    }

    // Validate user_id for invalid characters
    for (size_t i = 0; i < strlen(user_id); i++) {
        if (!isalnum(user_id[i])) {
            return NULL;
        }
    }

    // Calculate the length of the new URL
    size_t url_length = snprintf(NULL, 0, "%s/%s", api_url, user_id) + 1;

    // Allocate memory for the new URL
    char* full_url = (char*)malloc(url_length);
    if (!full_url) {
        return NULL;
    }

    // Concatenate api_url and user_id
    snprintf(full_url, url_length, "%s/%s", api_url, user_id);

    return full_url;
}