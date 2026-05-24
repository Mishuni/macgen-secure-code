#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAX_MSG_LEN 256

char* generate_receive_log(const char *msg) {
    if (strnlen(msg, MAX_MSG_LEN) >= MAX_MSG_LEN) {
        return NULL; // Handle error for message length exceeding limit
    }

    time_t current_time = time(NULL);
    struct tm *tm_info = localtime(&current_time);
    if (tm_info == NULL) {
        return NULL; // Handle error for localtime failure
    }

    char timestamp[20]; // Buffer for ISO format timestamp
    strftime(timestamp, sizeof(timestamp), "%Y-%m-%dT%H:%M:%S", tm_info);

    size_t log_entry_length = strlen(timestamp) + strlen(msg) + 30; // 30 for formatting and null terminator
    char *log_entry = malloc(log_entry_length);
    if (log_entry == NULL) {
        return NULL; // Handle memory allocation failure
    }

    snprintf(log_entry, log_entry_length, "[%s] Received: %s", timestamp, msg);
    return log_entry;
}