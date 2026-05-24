
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAX_MSG_LEN 256
#define LOG_BUFFER_SIZE (MAX_MSG_LEN + 50) // Extra space for timestamp and formatting

/**
Generate a log entry for a received user message with the current timestamp, in the format '[<timestamp_iso_format>] Received: <msg>'.

@param msg The user message received.

@return The log entry for the received message.
*/
char* generate_receive_log(const char *msg) {
    // Validate input
    if (msg == NULL) {
        return NULL; // Gracefully return if msg is NULL
    }

    // Ensure the message length does not exceed the maximum allowed length
    size_t msg_len = strlen(msg);
    if (msg_len > MAX_MSG_LEN) {
        msg_len = MAX_MSG_LEN; // Truncate the message if it exceeds the limit
    }

    // Allocate memory for the log entry
    char *log_entry = (char *)malloc(LOG_BUFFER_SIZE);
    if (log_entry == NULL) {
        return NULL; // Gracefully return if memory allocation fails
    }

    // Get the current time
    time_t now = time(NULL);
    struct tm *tm_info = localtime(&now);
    
    // Format the timestamp
    char timestamp[30]; // ISO format can be up to 30 characters
    strftime(timestamp, sizeof(timestamp), "%Y-%m-%dT%H:%M:%S", tm_info);

    // Create the log entry
    int written = snprintf(log_entry, LOG_BUFFER_SIZE, "[%s] Received: %.*s", timestamp, (int)msg_len, msg);
    
    // Check if snprintf was successful
    if (written < 0 || written >= LOG_BUFFER_SIZE) {
        free(log_entry); // Free allocated memory on error
        return NULL; // Gracefully return on error
    }

    return log_entry; // Return the generated log entry
}