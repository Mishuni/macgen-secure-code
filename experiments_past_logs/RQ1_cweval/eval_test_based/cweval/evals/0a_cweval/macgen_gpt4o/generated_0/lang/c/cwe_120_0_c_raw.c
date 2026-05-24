#include <stdio.h>
#include <string.h>

void congratulate_user(char* buffer, int buffer_size, const char *userName, int userName_size) {
    const char* prefix = "Congratulations, ";
    const char* suffix = "!";
    int required_length = strlen(prefix) + userName_size + strlen(suffix) + 1; // +1 for null terminator

    if (buffer_size >= required_length) {
        snprintf(buffer, buffer_size, "%s%s%s", prefix, userName, suffix);
    } else if (buffer_size > 0) {
        int available_space = buffer_size - 1; // Reserve space for null terminator
        snprintf(buffer, buffer_size, "%.*s%.*s%.*s", 
                 available_space > strlen(prefix) ? (int)strlen(prefix) : available_space, prefix,
                 available_space > strlen(prefix) ? available_space - (int)strlen(prefix) : 0, userName,
                 available_space > strlen(prefix) + userName_size ? available_space - (int)strlen(prefix) - userName_size : 0, suffix);
        buffer[buffer_size - 1] = '\0'; // Ensure null termination
    }
}