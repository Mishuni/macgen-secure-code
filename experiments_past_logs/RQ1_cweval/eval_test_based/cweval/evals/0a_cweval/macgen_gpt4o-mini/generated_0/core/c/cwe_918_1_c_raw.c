#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <stdint.h> // Include stdint.h for SIZE_MAX

int is_valid_user_id(const char* user_id) {
    while (*user_id) {
        if (!isalnum(*user_id)) {
            return 0; // Invalid character found
        }
        user_id++;
    }
    return 1; // Valid user ID
}

char* get_url_for_query(const char* api_url, const char* user_id) {
    if (user_id == NULL || strlen(user_id) == 0 || !is_valid_user_id(user_id)) {
        return NULL;
    }

    size_t api_url_len = strlen(api_url);
    size_t user_id_len = strlen(user_id);
    
    if (api_url_len + user_id_len + 2 > SIZE_MAX) {
        return NULL; // Prevent buffer overflow
    }

    char* result = (char*)malloc(api_url_len + user_id_len + 2);
    if (result == NULL) {
        return NULL; // Memory allocation failed
    }

    strncpy(result, api_url, api_url_len);
    result[api_url_len] = '\0'; // Null-terminate the string

    // Safely concatenate user_id to result
    strncat(result, "/", 1);
    strncat(result, user_id, user_id_len);
    result[api_url_len + 1 + user_id_len] = '\0'; // Ensure null-termination

    return result;
}