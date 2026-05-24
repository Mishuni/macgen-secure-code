
#include <stdio.h>

void print_message(const char* message) {
    if (message != NULL) {
        fputs(message, stdout);
    }
}