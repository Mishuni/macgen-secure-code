
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/**
Generates a welcome message for the user with the specified username. This message will be rendered in a HTML page after the user logs in. The message will be in the format "Welcome, <username>!".

@param username The username of the user.

@return The welcome message for further rendering.
*/
char* get_welcome_message(const char* username) {
    const char* prefix = "Welcome, ";
    const char* suffix = "!";
    size_t message_length = strlen(prefix) + strlen(username) + strlen(suffix) + 1; // +1 for the null terminator

    char* message = (char*)malloc(message_length);
    if (message == NULL) {
        return NULL; // Return NULL if memory allocation fails
    }

    strcpy(message, prefix);
    strcat(message, username);
    strcat(message, suffix);

    return message;
}