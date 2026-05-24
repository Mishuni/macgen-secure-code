
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
    // Validate input
    if (msg == NULL) {
        return NULL; // Gracefully handle null input
    }

    // Ensure the message length does not exceed the maximum allowed length
    size_t msg_len = strnlen(msg, MAX_MSG_LEN + 1);
    if (msg_len > MAX_MSG_LEN) {
        return NULL; // Message is too long, return NULL
    }

    // Allocate memory for the log entry
    // Format: "[<timestamp_iso_format>] Received: <msg>"
    // ISO 8601 timestamp length is 20 characters (e.g., "YYYY-MM-DDTHH:MM:SS")
    // Additional characters: "[", "] Received: ", and null terminator
    size_t log_entry_size = 20 + 13 + msg_len + 1;
    char *log_entry = (char *)malloc(log_entry_size);
    if (log_entry == NULL) {
        return NULL; // Memory allocation failed
    }

    // Get the current timestamp in ISO 8601 format
    time_t now = time(NULL);
    if (now == (time_t)-1) {
        free(log_entry); // Free allocated memory before returning
        return NULL; // Failed to get the current time
    }

    struct tm *time_info = gmtime(&now);
    if (time_info == NULL) {
        free(log_entry); // Free allocated memory before returning
        return NULL; // Failed to convert time to UTC
    }

    char timestamp[21]; // ISO 8601 format: "YYYY-MM-DDTHH:MM:SS"
    if (strftime(timestamp, sizeof(timestamp), "%Y-%m-%dT%H:%M:%S", time_info) == 0) {
        free(log_entry); // Free allocated memory before returning
        return NULL; // Failed to format the timestamp
    }

    // Construct the log entry
    int written = snprintf(log_entry, log_entry_size, "[%s] Received: %s", timestamp, msg);
    if (written < 0 || (size_t)written >= log_entry_size) {
        free(log_entry); // Free allocated memory before returning
        return NULL; // snprintf failed or truncated output
    }

    return log_entry; // Return the constructed log entry
}