#include <stdio.h>
#include <string.h>

void congratulate_user(char* buffer, int buffer_size, const char *userName, int userName_size)
{
    if (buffer == NULL || buffer_size <= 0) {
        return;
    }

    const char* message_prefix = "Congratulations, ";
    const int message_prefix_length = strlen(message_prefix);
    const int max_username_length = buffer_size - message_prefix_length - 1; // -1 for null terminator

    if (userName_size > max_username_length) {
        userName_size = max_username_length;
    }

    snprintf(buffer, buffer_size, "%s%.*s!", message_prefix, userName_size, userName);
}