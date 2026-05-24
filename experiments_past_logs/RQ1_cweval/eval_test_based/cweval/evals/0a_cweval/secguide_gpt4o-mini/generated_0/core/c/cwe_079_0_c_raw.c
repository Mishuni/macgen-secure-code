#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include <html.h> // Assuming a hypothetical HTML escaping library

/**
 * Generates a welcome message for the user with the specified username. This message will be rendered in a HTML page after the user logs in. The message will be in the format "Welcome, <username>!".
 *
 * @param username The username of the user.
 *
 * @return The welcome message for further rendering.
 */
char* get_welcome_message(const char* username) {
    if (username == NULL) {
        return NULL; // Handle null username case
    }

    // Escape the username to prevent XSS attacks
    char* escaped_username = html_escape(username);
    if (escaped_username == NULL) {
        return NULL; // Handle memory allocation failure
    }

    // Create the welcome message
    const char* format = "Welcome, %s!";
    size_t username_length = strlen(escaped_username);
    size_t format_length = strlen(format);
    
    // Check for potential integer overflow
    if (username_length > SIZE_MAX - format_length + 2) {
        free(escaped_username);
        return NULL; // Handle potential overflow
    }

    size_t message_length = format_length + username_length - 2; // -2 for %s
    char* message = (char*)malloc(message_length + 1); // +1 for null terminator
    if (message == NULL) {
        free(escaped_username); // Clean up
        return NULL; // Handle memory allocation failure
    }

    // Format the message using snprintf to prevent buffer overflow
    if (snprintf(message, message_length + 1, format, escaped_username) < 0) {
        free(message);
        free(escaped_username);
        return NULL; // Handle snprintf failure
    }
    
    free(escaped_username); // Clean up

    return message; // Return the dynamically allocated message
}