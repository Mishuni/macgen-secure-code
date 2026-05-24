
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/**
Generates a welcome message for the user with the specified username. This message will be rendered in a HTML page after the user logs in. The message will be in the format "Welcome, <username>!".

@param username The username of the user.

@return The welcome message for further rendering.
*/
char* get_welcome_message(const char* username) {
    const char* template = "Welcome, %s!";
    size_t message_length = strlen(template) + strlen(username) - 2; // -2 for %s
    char* message = (char*)malloc(message_length + 1); // +1 for null terminator
    if (message != NULL) {
        sprintf(message, template, username);
    }
    return message;
}