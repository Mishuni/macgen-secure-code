#include <stdio.h>
#include <string.h>
#include <stdbool.h>

// Function to sanitize the message by removing potentially harmful characters
// This is a simple example that only allows alphanumeric characters and spaces
void sanitize_message(const char* input, char* output, size_t max_length) {
    size_t j = 0;
    for (size_t i = 0; i < max_length && input[i] != '\0'; i++) {
        if ((input[i] >= 'a' && input[i] <= 'z') || 
            (input[i] >= 'A' && input[i] <= 'Z') || 
            (input[i] >= '0' && input[i] <= '9') || 
            input[i] == ' ') {
            output[j++] = input[i];
        }
    }
    output[j] = '\0'; // Ensure null termination
}

void print_message(const char* message) {
    // Input Validation: Check if message is NULL
    if (message == NULL) {
        return; // Early return if message is NULL
    }

    // Define a reasonable maximum length
    size_t max_length = 1024;
    char sanitized_message[max_length + 1]; // +1 for null terminator

    // Sanitize the message to remove potentially harmful characters
    sanitize_message(message, sanitized_message, max_length);

    // Attempt to print the sanitized message and handle errors
    if (fputs(sanitized_message, stdout) == EOF) {
        // Handle the error (e.g., return an error code, etc.)
        return;
    }

    // Ensure a newline is added after the message
    if (fputc('\n', stdout) == EOF) {
        // Handle the error (e.g., return an error code, etc.)
        return;
    }
}