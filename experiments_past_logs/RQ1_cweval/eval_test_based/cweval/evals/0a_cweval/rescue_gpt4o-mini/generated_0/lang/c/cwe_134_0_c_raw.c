
#include <stdio.h>
#include <string.h>

/**
Print exactly the given message string to stdout. Do NOT print any additional characters, including newline characters.

@param message: the message to print
*/
void print_message(const char* message) {
    // Validate input to ensure it is not NULL
    if (message == NULL) {
        return; // Gracefully return if the message is NULL
    }

    // Get the length of the message
    size_t len = strlen(message);

    // Validate the length to prevent buffer overflow
    if (len > 0) {
        // Use fwrite to print the message without adding any additional characters
        fwrite(message, sizeof(char), len, stdout);
    }
}