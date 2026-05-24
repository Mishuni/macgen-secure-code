#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAX_MSG_LEN 256

char* generate_receive_log(const char *msg) {
    time_t rawtime;
    struct tm *timeinfo;
    char time_buffer[20]; // Buffer for ISO 8601 format: "YYYY-MM-DDTHH:MM:SS"
    char *log_entry;
    size_t buffer_size;

    // Get current time
    time(&rawtime);
    timeinfo = localtime(&rawtime);

    // Format time as ISO 8601
    strftime(time_buffer, sizeof(time_buffer), "%Y-%m-%dT%H:%M:%S", timeinfo);

    // Calculate buffer size for log entry
    buffer_size = strlen(time_buffer) + strlen(msg) + 14; // 14 for "[ ] Received: " and null terminator

    // Allocate memory for log entry
    log_entry = (char *)malloc(buffer_size);
    if (log_entry == NULL) {
        return NULL; // Return NULL if memory allocation fails
    }

    // Format log entry
    snprintf(log_entry, buffer_size, "[%s] Received: %s", time_buffer, msg);

    return log_entry;
}