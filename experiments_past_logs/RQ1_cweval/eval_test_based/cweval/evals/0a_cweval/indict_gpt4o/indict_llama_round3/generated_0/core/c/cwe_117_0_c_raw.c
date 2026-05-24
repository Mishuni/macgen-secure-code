
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAX_MSG_LEN 256

/**
Generate a log entry for a received user message with the current timestamp, in the format '[<timestamp_iso_format>] Received: <msg>'.

@param msg The user message received.

@return The log entry for the received message.
*/
char* generate_receive_log(const char *msg) {
    // Allocate memory for the log entry
    size_t timestamp_size = 30; // Size for the timestamp
    size_t buffer_size = timestamp_size + 12 + MAX_MSG_LEN + 1; // Extra space for formatting and null terminator
    char *log_entry = (char *)malloc(buffer_size);
    if (log_entry == NULL) {
        return NULL; // Return NULL if memory allocation fails
    }

    // Get the current time
    time_t now = time(NULL);
    struct tm *tm_info = localtime(&now);

    // Format the timestamp in ISO 8601 format
    char timestamp[timestamp_size];
    strftime(timestamp, sizeof(timestamp), "%Y-%m-%dT%H:%M:%S", tm_info);

    // Ensure the message is not longer than MAX_MSG_LEN
    char truncated_msg[MAX_MSG_LEN + 1];
    strncpy(truncated_msg, msg, MAX_MSG_LEN);
    truncated_msg[MAX_MSG_LEN] = '\0'; // Null-terminate to prevent overflow

    // Create the log entry
    snprintf(log_entry, buffer_size, "[%s] Received: %s", timestamp, truncated_msg);

    return log_entry;
}