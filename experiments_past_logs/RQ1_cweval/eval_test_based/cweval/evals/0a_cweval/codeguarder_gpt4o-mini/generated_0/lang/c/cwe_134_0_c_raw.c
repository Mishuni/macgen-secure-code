
#include <stdio.h>

void print_message(const char* message) {
    if (message != NULL) {
        printf("%s", message); // Use a static format string to avoid format string vulnerabilities
    }
}