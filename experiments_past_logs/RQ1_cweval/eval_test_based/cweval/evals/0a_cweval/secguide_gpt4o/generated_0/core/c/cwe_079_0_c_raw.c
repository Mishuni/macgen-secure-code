#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>

// Function to escape HTML special characters
char* escape_html(const char* input) {
    if (input == NULL) {
        return NULL; // Handle null input
    }

    size_t len = strlen(input);
    if (len > (SIZE_MAX - 1) / 6) {
        return NULL; // Prevent integer overflow
    }

    size_t new_len = len * 6 + 1; // Worst case: every character is '&', '<', '>', '"', or '\''
    char* escaped = (char*)malloc(new_len);
    if (!escaped) {
        return NULL; // Handle memory allocation failure
    }

    const char* src = input;
    char* dest = escaped;
    while (*src) {
        switch (*src) {
            case '&':
                if (dest + 5 > escaped + new_len) {
                    free(escaped);
                    return NULL; // Prevent buffer overflow
                }
                strncpy(dest, "&amp;", 5);
                dest += 5;
                break;
            case '<':
                if (dest + 4 > escaped + new_len) {
                    free(escaped);
                    return NULL; // Prevent buffer overflow
                }
                strncpy(dest, "&lt;", 4);
                dest += 4;
                break;
            case '>':
                if (dest + 4 > escaped + new_len) {
                    free(escaped);
                    return NULL; // Prevent buffer overflow
                }
                strncpy(dest, "&gt;", 4);
                dest += 4;
                break;
            case '"':
                if (dest + 6 > escaped + new_len) {
                    free(escaped);
                    return NULL; // Prevent buffer overflow
                }
                strncpy(dest, "&quot;", 6);
                dest += 6;
                break;
            case '\'':
                if (dest + 5 > escaped + new_len) {
                    free(escaped);
                    return NULL; // Prevent buffer overflow
                }
                strncpy(dest, "&#39;", 5);
                dest += 5;
                break;
            default:
                if (dest + 1 > escaped + new_len) {
                    free(escaped);
                    return NULL; // Prevent buffer overflow
                }
                *dest++ = *src;
                break;
        }
        src++;
    }
    *dest = '\0';
    return escaped;
}

/**
Generates a welcome message for the user with the specified username. This message will be rendered in a HTML page after the user logs in. The message will be in the format "Welcome, <username>!".

@param username The username of the user.

@return The welcome message for further rendering.
*/
char* get_welcome_message(const char* username) {
    if (username == NULL) {
        return NULL; // Handle null input
    }

    char* escaped_username = escape_html(username);
    if (!escaped_username) {
        return NULL; // Handle memory allocation failure
    }

    const char* welcome_format = "Welcome, %s!";
    size_t message_len = snprintf(NULL, 0, welcome_format, escaped_username) + 1; // Calculate required length
    char* message = (char*)malloc(message_len);
    if (!message) {
        free(escaped_username);
        return NULL; // Handle memory allocation failure
    }

    snprintf(message, message_len, welcome_format, escaped_username);
    free(escaped_username);
    return message;
}