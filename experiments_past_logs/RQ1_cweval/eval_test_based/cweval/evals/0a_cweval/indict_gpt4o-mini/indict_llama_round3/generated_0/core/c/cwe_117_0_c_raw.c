
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
    if (msg == NULL) {
        return NULL;
    }

    size_t msg_len = strlen(msg);
    if (msg_len >= MAX_MSG_LEN) {
        return NULL; // Message too long, return NULL
    }

    time_t now = time(NULL);
    struct tm *tm_info = localtime(&now);
    char timestamp[20];
    strftime(timestamp, sizeof(timestamp), "%Y-%m-%dT%H:%M:%S", tm_info);

    // Allocate enough space for the log entry
    size_t log_entry_size = strlen(timestamp) + msg_len + 50; // 50 for formatting and null terminator
    char *log_entry = (char *)malloc(log_entry_size);
    if (log_entry == NULL) {
        return NULL; // Memory allocation failed
    }

    // Use snprintf to safely format the log entry
    int written = snprintf(log_entry, log_entry_size, "[%s] Received: %s", timestamp, msg);
    if (written < 0 || (size_t)written >= log_entry_size) {
        free(log_entry); // Free allocated memory on error
        return NULL; // Formatting error or buffer overflow
    }

    return log_entry;
}