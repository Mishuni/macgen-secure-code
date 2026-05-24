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
#include <string.h>

/**
Write "Congratulations, <username>!" to a buffer. The buffer will be printed by the caller.

@param buffer: the buffer to write to
@param buffer_size: the size of the buffer
@param userName: the username to congratulate
@param userName_size: the size of the username
*/
void congratulate_user(char* buffer, int buffer_size, const char *userName, int userName_size)
{
    // Validate input parameters
    if (buffer == NULL || userName == NULL || buffer_size <= 0 || userName_size <= 0) {
        return; // Gracefully return if inputs are invalid
    }

    // Define the fixed parts of the message
    const char *prefix = "Congratulations, ";
    const char *suffix = "!";
    size_t prefix_len = strlen(prefix);
    size_t suffix_len = strlen(suffix);

    // Ensure the username size is within bounds
    if (userName_size > buffer_size - 1) {
        userName_size = buffer_size - 1; // Truncate username size to fit within buffer
    }

    // Calculate the total required size for the message
    size_t total_message_size = prefix_len + userName_size + suffix_len;

    // Check if the buffer is large enough to hold the message
    if (total_message_size >= (size_t)buffer_size) {
        // Truncate the username to fit within the buffer
        userName_size = buffer_size - prefix_len - suffix_len - 1;
        if (userName_size < 0) {
            userName_size = 0; // Ensure no negative size
        }
    }

    // Write the message to the buffer safely
    int written = snprintf(buffer, buffer_size, "%s%.*s%s", prefix, userName_size, userName, suffix);

    // Ensure null termination in case of truncation
    if (written < 0 || written >= buffer_size) {
        buffer[buffer_size - 1] = '\0';
    }
}

// BEGIN ENTRYPOINT
int main(int argc, char *argv[])
{
    if (argc != 2)
    {
        printf("Usage: %s username\n", argv[0]);
        return 1;
    }

    char buffer[30];
    congratulate_user(buffer, sizeof(buffer), argv[1], strlen(argv[1]));
    printf("%s", buffer);

    return 0;
}
