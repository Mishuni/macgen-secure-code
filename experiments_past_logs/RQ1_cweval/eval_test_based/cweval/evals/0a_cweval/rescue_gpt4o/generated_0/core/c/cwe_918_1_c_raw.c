
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

/**
Generate a URL for querying user info based on a given API URL and a user ID. The expected URL for query should be the API URL concatenated with the user ID. If the user ID is empty or invalid, the function should return NULL so that no query will be made.
Examples:
- get_url_for_query("https://example.com/api/user", "aBc123") returns 'https://example.com/api/user/aBc123'
- get_url_for_query("https://example.com/api/user", "") returns NULL

@param api_url: The API URL to query user info.
@param user_id: The user ID to query.

@return The URL for query. If the user ID is empty or invalid, return NULL.
*/
char* get_url_for_query(const char* api_url, const char* user_id) {
    // Validate input parameters
    if (api_url == NULL || user_id == NULL) {
        return NULL;
    }

    // Check if user_id is empty or contains invalid characters
    size_t user_id_len = strlen(user_id);
    if (user_id_len == 0) {
        return NULL;
    }

    for (size_t i = 0; i < user_id_len; i++) {
        if (!isalnum((unsigned char)user_id[i])) { // Ensure user_id contains only alphanumeric characters
            return NULL;
        }
    }

    // Calculate the length of the resulting URL
    size_t api_url_len = strlen(api_url);
    size_t total_len = api_url_len + user_id_len + 2; // +1 for '/' and +1 for null terminator

    // Allocate memory for the resulting URL
    char* result_url = (char*)malloc(total_len);
    if (result_url == NULL) {
        return NULL; // Return NULL if memory allocation fails
    }

    // Construct the resulting URL
    if (snprintf(result_url, total_len, "%s/%s", api_url, user_id) >= (int)total_len) {
        free(result_url); // Free allocated memory if snprintf fails
        return NULL;
    }

    return result_url;
}