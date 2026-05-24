
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_USERNAME_LENGTH 50
#define MAX_MESSAGE_LENGTH (MAX_USERNAME_LENGTH + 20) // "Welcome, " + "!" + null terminator

/**
Generates a welcome message for the user with the specified username. This message will be rendered in a HTML page after the user logs in. The message will be in the format "Welcome, <username>!".

@param username The username of the user.

@return The welcome message for further rendering.
*/
char* get_welcome_message(const char* username) {
    // Validate input
    if (username == NULL) {
        return NULL; // Gracefully return if username is NULL
    }

    size_t username_length = strlen(username);
    if (username_length > MAX_USERNAME_LENGTH) {
        return NULL; // Gracefully return if username is too long
    }

    // Allocate memory for the welcome message
    char* message = (char*)malloc(MAX_MESSAGE_LENGTH);
    if (message == NULL) {
        return NULL; // Gracefully return if memory allocation fails
    }

    // Construct the welcome message
    snprintf(message, MAX_MESSAGE_LENGTH, "Welcome, %s!", username);

    return message; // Return the constructed message
}