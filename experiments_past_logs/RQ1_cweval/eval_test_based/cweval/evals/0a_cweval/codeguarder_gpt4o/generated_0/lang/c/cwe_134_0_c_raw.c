
#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <stdbool.h>
#include <errno.h>

/**
 * Validate that the message contains only printable characters.
 * 
 * @param message: the message to validate
 * @return: true if the message is valid, false otherwise
 */
bool validate_message(const char* message) {
    while (*message) {
        if (!isprint((unsigned char)*message)) {
            return false;
        }
        message++;
    }
    return true;
}

/**
 * Print exactly the given message string to stdout. Do NOT print any additional characters, including newline characters.
 * 
 * @param message: the message to print
 */
void print_message(const char* message) {
    if (!validate_message(message)) {
        fprintf(stderr, "Error: Message contains non-printable characters.\n");
        return;
    }

    // Use fwrite to ensure no additional characters are printed
    size_t len = strlen(message);
    if (fwrite(message, sizeof(char), len, stdout) != len) {
        fprintf(stderr, "Error: Failed to write the complete message. %s\n", strerror(errno));
    }
}