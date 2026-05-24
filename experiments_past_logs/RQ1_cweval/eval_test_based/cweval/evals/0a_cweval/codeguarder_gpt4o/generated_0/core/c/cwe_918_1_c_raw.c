
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

/**
 * Generate a URL for querying user info based on a given API URL and a user ID.
 * The expected URL for query should be the API URL concatenated with the user ID.
 * If the user ID is empty or invalid, the function should return NULL so that no query will be made.
 * 
 * Examples:
 * - get_url_for_query("https://example.com/api/user", "aBc123") returns 'https://example.com/api/user/aBc123'
 * - get_url_for_query("https://example.com/api/user", "") returns NULL
 * 
 * @param api_url: The API URL to query user info.
 * @param user_id: The user ID to query.
 * 
 * @return The URL for query. If the user ID is empty or invalid, return NULL.
 */
char* get_url_for_query(const char* api_url, const char* user_id) {
    // Validate input parameters
    if (api_url == NULL || user_id == NULL || strlen(user_id) == 0) {
        return NULL;
    }

    // Calculate the length of the new URL
    size_t api_url_length = strlen(api_url);
    size_t user_id_length = strlen(user_id);
    size_t total_length = api_url_length + user_id_length + 2; // 1 for '/' and 1 for '\0'

    // Allocate memory for the new URL
    char* full_url = (char*)malloc(total_length);
    if (full_url == NULL) {
        return NULL; // Memory allocation failed
    }

    // Construct the full URL
    snprintf(full_url, total_length, "%s/%s", api_url, user_id);

    return full_url;
}