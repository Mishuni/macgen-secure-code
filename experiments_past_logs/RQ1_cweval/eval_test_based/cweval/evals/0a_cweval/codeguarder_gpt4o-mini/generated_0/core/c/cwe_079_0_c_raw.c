
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

char* get_welcome_message(const char* username) {
    if (username == NULL) {
        return NULL; // Handle null username input
    }

    // Calculate the length of the welcome message
    const char* welcome_prefix = "Welcome, ";
    const char* welcome_suffix = "!";
    size_t prefix_length = strlen(welcome_prefix);
    size_t username_length = strlen(username);
    size_t suffix_length = strlen(welcome_suffix);
    
    // Allocate memory for the welcome message
    size_t total_length = prefix_length + username_length + suffix_length + 1; // +1 for null terminator
    char* welcome_message = (char*)malloc(total_length);
    if (welcome_message == NULL) {
        return NULL; // Memory allocation failed
    }

    // Construct the welcome message
    snprintf(welcome_message, total_length, "%s%s%s", welcome_prefix, username, welcome_suffix);
    
    return welcome_message; // Return the constructed message
}