#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <ctype.h>

#define MAX_MSG_LEN 256
#define TIMESTAMP_SIZE 20
#define LOG_ENTRY_BUFFER_SIZE 50

/**
Generate a log entry for a received user message with the current timestamp, in the format '[<timestamp_iso_format>] Received: <msg>'.

@param msg The user message received.

@return The log entry for the received message.
*/
char* generate_receive_log(const char *msg) {
    if (msg == NULL || strlen(msg) == 0 || strlen(msg) > MAX_MSG_LEN) {
        return NULL; // Handle invalid input
    }

    // Validate content of msg to prevent log injection
    for (size_t i = 0; i < strlen(msg); i++) {
        if (msg[i] < 32 || msg[i] > 126) { // Check for control characters
            return NULL; // Invalid character found
        }
    }

    // Get current time
    time_t now = time(NULL);
    struct tm tm_info;
    localtime_r(&now, &tm_info); // Use thread-safe version

    // Format timestamp
    char timestamp[TIMESTAMP_SIZE];
    strftime(timestamp, sizeof(timestamp), "%Y-%m-%dT%H:%M:%S", &tm_info);

    // Create log entry
    size_t log_entry_size = strlen(timestamp) + strlen(msg) + LOG_ENTRY_BUFFER_SIZE + 1; // +1 for null terminator
    char *log_entry = (char *)malloc(log_entry_size);
    if (log_entry == NULL) {
        return NULL; // Handle memory allocation failure
    }

    snprintf(log_entry, log_entry_size, "[%s] Received: %s", timestamp, msg);
    
    return log_entry; // Caller is responsible for freeing the allocated memory
}