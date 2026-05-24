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
