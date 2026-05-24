
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char* get_url_for_query(const char* api_url, const char* user_id) {
    // Check if user_id is NULL or empty
    if (user_id == NULL || strlen(user_id) == 0) {
        return NULL;
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