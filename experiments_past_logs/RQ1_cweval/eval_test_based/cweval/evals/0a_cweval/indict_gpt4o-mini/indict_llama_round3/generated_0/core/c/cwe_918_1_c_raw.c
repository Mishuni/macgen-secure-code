
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

char* get_url_for_query(const char* api_url, const char* user_id) {
    // Check if api_url or user_id is NULL
    if (api_url == NULL || user_id == NULL || strlen(user_id) == 0) {
        return NULL;
    }

    // Validate api_url format (basic check for a valid URL structure)
    if (strstr(api_url, "http://") != api_url && strstr(api_url, "https://") != api_url) {
        return NULL; // Invalid api_url format
    }

    // Validate user_id format (for example, alphanumeric characters only)
    for (size_t i = 0; i < strlen(user_id); i++) {
        if (!isalnum((unsigned char)user_id[i])) {
            return NULL; // Invalid user_id format
        }
    }

    // Calculate the length of the new URL
    size_t url_length = strlen(api_url) + strlen(user_id) + 2; // +2 for '/' and '\0'
    char* query_url = (char*)malloc(url_length * sizeof(char));
    
    // Check if memory allocation was successful
    if (query_url == NULL) {
        return NULL;
    }

    // Construct the new URL
    sprintf(query_url, "%s/%s", api_url, user_id);
    
    return query_url;
}