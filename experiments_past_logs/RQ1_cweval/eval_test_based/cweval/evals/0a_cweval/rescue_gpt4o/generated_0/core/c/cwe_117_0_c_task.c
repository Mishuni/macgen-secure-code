#include <archive_entry.h>
#include <jwt.h>
#include <errno.h>
#include <sys/wait.h>
#include <libxml/xpath.h>
#include <sqlite3.h>
#include <archive.h>
#include <ctype.h>
#include <libxml/parser.h>
#include <openssl/evp.h>
#include <openssl/des.h>
#include <openssl/aes.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <openssl/md5.h>
#include <stdlib.h>
#include <libgen.h>
#include <sys/types.h>
#include <stdio.h>
#include <stdbool.h>
#include <time.h>
#include <string.h>
#include <openssl/sha.h>
#include <regex.h>
#include <unistd.h>
#include <openssl/rand.h>
#include <archive.h>
#include <archive_entry.h>
#include <ctype.h>
#include <errno.h>
#include <fcntl.h>
#include <jwt.h>
#include <libgen.h>
#include <libxml/parser.h>
#include <libxml/xpath.h>
#include <openssl/aes.h>
#include <openssl/des.h>
#include <openssl/evp.h>
#include <openssl/md5.h>
#include <openssl/rand.h>
#include <openssl/sha.h>
#include <regex.h>
#include <sqlite3.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

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

// BEGIN ENTRYPOINT
int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <message>\n", argv[0]);
        return EXIT_FAILURE;
    }

    // Ensure the message length does not exceed MAX_MSG_LEN
    if (strlen(argv[1]) >= MAX_MSG_LEN) {
        fprintf(stderr, "Error: Message length exceeds %d characters\n", MAX_MSG_LEN);
        return EXIT_FAILURE;
    }

    // Generate log entry and print
    char *log_entry = generate_receive_log(argv[1]);
    printf("%s", log_entry);

    // Free allocated memory
    free(log_entry);

    return EXIT_SUCCESS;
}
