#include <stdio.h>
#include <string.h>

#define MAX_MESSAGE_LENGTH 1024

int print_message(const char* message) {
    if (message == NULL) {
        return -1; // Indicate error for NULL message
    }

    size_t length = strlen(message);
    if (length > MAX_MESSAGE_LENGTH) {
        return -2; // Indicate error for message too long
    }

    // Use fwrite to limit the number of characters written to stdout
    if (fwrite(message, sizeof(char), length, stdout) < length) {
        return -3; // Indicate error on fwrite failure
    }

    return 0; // Indicate success
}