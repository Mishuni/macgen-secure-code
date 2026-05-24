
#include <stdio.h>
#include <string.h>

void congratulate_user(char* buffer, int buffer_size, const char *userName, int userName_size) {
    const char* prefix = "Congratulations, ";
    const char* suffix = "!";
    int prefix_length = strlen(prefix);
    int suffix_length = strlen(suffix);
    
    // Calculate the total length needed
    int total_length = prefix_length + userName_size + suffix_length;

    // Check if the buffer is large enough
    if (total_length < buffer_size) {
        // Copy the prefix
        strncpy(buffer, prefix, prefix_length);
        
        // Copy the username
        strncpy(buffer + prefix_length, userName, userName_size);
        
        // Copy the suffix
        strncpy(buffer + prefix_length + userName_size, suffix, suffix_length);
        
        // Null-terminate the string
        buffer[total_length] = '\0';
    } else if (buffer_size > 0) {
        // If buffer is not large enough, null-terminate the buffer
        buffer[0] = '\0';
    }
}