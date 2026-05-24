
#include <stdio.h>
#include <string.h>

void congratulate_user(char* buffer, int buffer_size, const char *userName, int userName_size)
{
    const char* message_format = "Congratulations, %s!";
    int message_length = snprintf(NULL, 0, message_format, userName);
    
    if (message_length + 1 > buffer_size) {
        // If the buffer is too small, we can choose to handle it in various ways.
        // Here we will simply not write anything to the buffer.
        return;
    }
    
    snprintf(buffer, buffer_size, message_format, userName);
}