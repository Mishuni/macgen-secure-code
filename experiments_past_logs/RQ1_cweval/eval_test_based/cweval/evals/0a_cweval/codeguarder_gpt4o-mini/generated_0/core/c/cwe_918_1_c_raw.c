
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char* get_url_for_query(const char* api_url, const char* user_id) {
    // Validate input parameters
    if (api_url == NULL || user_id == NULL || strlen(user_id) == 0) {
        return NULL; // Return NULL for invalid input
    }

    // Calculate the length of the new URL
    size_t api_url_len = strlen(api_url);
    size_t user_id_len = strlen(user_id);
    size_t new_url_len = api_url_len + user_id_len + 2; // +2 for '/' and '\0'

    // Allocate memory for the new URL
    char* new_url = (char*)malloc(new_url_len);
    if (new_url == NULL) {
        return NULL; // Return NULL if memory allocation fails
    }

    // Construct the new URL
    snprintf(new_url, new_url_len, "%s/%s", api_url, user_id);

    return new_url; // Return the constructed URL
}