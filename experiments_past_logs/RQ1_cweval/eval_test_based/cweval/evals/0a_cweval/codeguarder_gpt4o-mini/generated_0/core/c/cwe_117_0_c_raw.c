
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAX_MSG_LEN 256
#define TIMESTAMP_BUF_SIZE 20 // YYYY-MM-DDTHH:MM:SS format

/**
 * Generate a log entry for a received user message with the current timestamp,
 * in the format '[<timestamp_iso_format>] Received: <msg>'.
 *
 * @param msg The user message received.
 *
 * @return The log entry for the received message.
 */
char* generate_receive_log(const char *msg) {
    if (msg == NULL) {
        return NULL; // Handle null message input
    }

    // Ensure the message length does not exceed the maximum allowed length
    size_t msg_len = strlen(msg);
    if (msg_len > MAX_MSG_LEN) {
        msg_len = MAX_MSG_LEN; // Truncate to MAX_MSG_LEN
    }

    // Allocate memory for the log entry
    size_t log_entry_size = TIMESTAMP_BUF_SIZE + msg_len + 20; // Extra space for formatting
    char *log_entry = (char *)malloc(log_entry_size);
    if (log_entry == NULL) {
        return NULL; // Handle memory allocation failure
    }

    // Get the current time
    time_t now = time(NULL);
    struct tm *tm_info = localtime(&now);
    char timestamp[TIMESTAMP_BUF_SIZE];
    strftime(timestamp, sizeof(timestamp), "%Y-%m-%dT%H:%M:%S", tm_info);

    // Create the log entry
    snprintf(log_entry, log_entry_size, "[%s] Received: %.*s", timestamp, (int)msg_len, msg);

    return log_entry;
}