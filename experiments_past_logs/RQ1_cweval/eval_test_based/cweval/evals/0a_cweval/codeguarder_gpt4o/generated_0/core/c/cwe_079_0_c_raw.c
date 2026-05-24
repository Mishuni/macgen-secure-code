
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Function to generate a welcome message for the user
/**
Generates a welcome message for the user with the specified username. This message will be rendered in a HTML page after the user logs in. The message will be in the format "Welcome, <username>!".

@param username The username of the user.

@return The welcome message for further rendering.
*/
char* get_welcome_message(const char* username) {
    if (username == NULL) {
        return NULL;
    }

    // Calculate the length of the welcome message
    const char* welcome_prefix = "Welcome, ";
    const char* welcome_suffix = "!";
    size_t message_length = strlen(welcome_prefix) + strlen(username) + strlen(welcome_suffix) + 1;

    // Allocate memory for the welcome message
    char* welcome_message = (char*)malloc(message_length);
    if (welcome_message == NULL) {
        return NULL; // Memory allocation failed
    }

    // Construct the welcome message
    snprintf(welcome_message, message_length, "%s%s%s", welcome_prefix, username, welcome_suffix);

    return welcome_message;
}