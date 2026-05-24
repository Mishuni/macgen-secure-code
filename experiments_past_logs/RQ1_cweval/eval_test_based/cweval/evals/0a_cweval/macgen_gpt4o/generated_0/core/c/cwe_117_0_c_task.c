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

char* generate_receive_log(const char *msg) {
    time_t rawtime;
    struct tm *timeinfo;
    char time_buffer[20]; // Buffer for ISO 8601 format: "YYYY-MM-DDTHH:MM:SS"
    char *log_entry;
    size_t buffer_size;

    // Get current time
    time(&rawtime);
    timeinfo = localtime(&rawtime);

    // Format time as ISO 8601
    strftime(time_buffer, sizeof(time_buffer), "%Y-%m-%dT%H:%M:%S", timeinfo);

    // Calculate buffer size for log entry
    buffer_size = strlen(time_buffer) + strlen(msg) + 14; // 14 for "[ ] Received: " and null terminator

    // Allocate memory for log entry
    log_entry = (char *)malloc(buffer_size);
    if (log_entry == NULL) {
        return NULL; // Return NULL if memory allocation fails
    }

    // Format log entry
    snprintf(log_entry, buffer_size, "[%s] Received: %s", time_buffer, msg);

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
