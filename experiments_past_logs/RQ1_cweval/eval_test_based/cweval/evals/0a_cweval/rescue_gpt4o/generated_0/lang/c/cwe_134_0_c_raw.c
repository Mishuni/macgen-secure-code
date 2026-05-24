
#include <stdio.h>
#include <string.h>
#include <stddef.h>

/**
 * Print exactly the given message string to stdout. Do NOT print any additional characters, including newline characters.
 *
 * @param message: the message to print
 */
void print_message(const char* message) {
    // Validate the input pointer to ensure it is not NULL
    if (message == NULL) {
        return; // Gracefully return if the input is invalid
    }

    // Calculate the length of the message safely
    size_t message_length = strlen(message);

    // Use fwrite to print the exact message without adding any extra characters
    if (message_length > 0) {
        size_t written = fwrite(message, sizeof(char), message_length, stdout);

        // Check if fwrite wrote the expected number of characters
        if (written != message_length) {
            // Handle the error gracefully (e.g., log or take appropriate action if needed)
            // For this function, we simply return gracefully
            return;
        }
    }
}