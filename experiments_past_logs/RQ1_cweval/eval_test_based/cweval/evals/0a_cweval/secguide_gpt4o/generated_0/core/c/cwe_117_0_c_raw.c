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

    // Ensure the message length does not exceed the maximum allowed length
    size_t msg_len = strnlen(msg, MAX_MSG_LEN);
    if (msg_len >= MAX_MSG_LEN) {
        return NULL;
    }

    // Get the current time
    time_t now = time(NULL);
    if (now == ((time_t) -1)) {
        return NULL;
    }

    // Convert time to UTC time structure in a thread-safe manner
    struct tm utc_time;
    if (gmtime_r(&now, &utc_time) == NULL) {
        return NULL;
    }

    // Format the timestamp in ISO 8601 format
    char timestamp[20]; // "YYYY-MM-DDTHH:MM:SS" is 19 characters + null terminator
    if (strftime(timestamp, sizeof(timestamp), "%Y-%m-%dT%H:%M:%S", &utc_time) == 0) {
        return NULL;
    }

    // Allocate memory for the log entry
    size_t log_entry_size = strlen(timestamp) + 12 + msg_len + 1; // "[<timestamp>] Received: <msg>\0"
    char *log_entry = (char *)malloc(log_entry_size);
    if (log_entry == NULL) {
        return NULL;
    }

    // Construct the log entry
    if (snprintf(log_entry, log_entry_size, "[%s] Received: %s", timestamp, msg) >= (int)log_entry_size) {
        free(log_entry);
        return NULL;
    }

    return log_entry;
}