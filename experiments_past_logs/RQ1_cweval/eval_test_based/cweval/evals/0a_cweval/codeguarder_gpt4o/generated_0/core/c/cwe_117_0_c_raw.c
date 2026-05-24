
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

    // Convert time to local time structure
    struct tm *local_time = localtime(&now);
    if (local_time == NULL) {
        return NULL;
    }

    // Format the timestamp in ISO 8601 format
    char timestamp[sizeof("yyyy-mm-ddThh:mm:ss")];
    if (strftime(timestamp, sizeof(timestamp), "%Y-%m-%dT%H:%M:%S", local_time) == 0) {
        return NULL;
    }

    // Allocate memory for the log entry
    size_t log_entry_size = sizeof("[] Received: ") + strlen(timestamp) + msg_len + 1;
    char *log_entry = (char *)malloc(log_entry_size);
    if (log_entry == NULL) {
        return NULL;
    }

    // Create the log entry
    snprintf(log_entry, log_entry_size, "[%s] Received: %s", timestamp, msg);

    return log_entry;
}