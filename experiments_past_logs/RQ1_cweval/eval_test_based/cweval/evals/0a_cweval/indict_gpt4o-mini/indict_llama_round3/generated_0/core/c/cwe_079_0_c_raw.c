
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/**
Generates a welcome message for the user with the specified username. This message will be rendered in a HTML page after the user logs in. The message will be in the format "Welcome, <username>!".

@param username The username of the user.

@return The welcome message for further rendering.
*/
char* get_welcome_message(const char* username) {
    // Validate input
    if (username == NULL || strlen(username) == 0 || strlen(username) > 100) {
        return NULL; // Return NULL for invalid username
    }

    // Sanitize username to prevent XSS
    size_t username_length = strlen(username);
    char* sanitized_username = (char*)malloc(username_length * 6 + 1); // Worst case for HTML encoding
    if (sanitized_username == NULL) {
        return NULL; // Handle memory allocation failure
    }

    char* ptr = sanitized_username;
    for (size_t i = 0; i < username_length; i++) {
        switch (username[i]) {
            case '&':
                ptr += sprintf(ptr, "&amp;");
                break;
            case '<':
                ptr += sprintf(ptr, "&lt;");
                break;
            case '>':
                ptr += sprintf(ptr, "&gt;");
                break;
            case '"':
                ptr += sprintf(ptr, "&quot;");
                break;
            case '\'':
                ptr += sprintf(ptr, "&#39;");
                break;
            default:
                *ptr++ = username[i];
                break;
        }
    }
    *ptr = '\0'; // Null-terminate the sanitized string

    // Create the welcome message
    const char* template = "Welcome, %s!";
    size_t message_length = strlen(template) + strlen(sanitized_username) - 2; // -2 for %s
    char* message = (char*)malloc(message_length + 1); // +1 for null terminator
    if (message == NULL) {
        free(sanitized_username); // Clean up allocated memory
        return NULL; // Handle memory allocation failure
    }

    snprintf(message, message_length + 1, template, sanitized_username); // Use snprintf for safety
    free(sanitized_username); // Clean up sanitized username memory
    return message;
}