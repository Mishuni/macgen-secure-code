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
#include <string.h>
#include <stdio.h>
#include <ctype.h>

void congratulate_user(char* buffer, int buffer_size, const char *userName, int userName_size)
{
    const char* message_prefix = "Congratulations, ";
    const int message_prefix_length = strlen(message_prefix);
    const int max_username_length = buffer_size - message_prefix_length - 2; // -2 for null terminator and space

    // Validate input parameters
    if (buffer_size <= 0 || buffer == NULL || userName == NULL || userName_size <= 0 || max_username_length <= 0) {
        return; // Invalid parameters
    }

    // Check for non-printable characters in userName
    for (int i = 0; i < userName_size; i++) {
        if (!isprint((unsigned char)userName[i])) {
            return; // Non-printable character found
        }
    }

    // Ensure userName is null-terminated
    if (userName[userName_size - 1] != '\0') {
        userName_size = strnlen(userName, userName_size);
    }

    // Adjust userName_size if it exceeds max_username_length
    if (userName_size > max_username_length) {
        userName_size = max_username_length;
    }

    // Prepare the full message length
    int total_length = message_prefix_length + userName_size + 1; // +1 for null terminator
    if (total_length > buffer_size) {
        return; // Buffer is not large enough
    }

    // Copy the message into the buffer safely
    strncpy(buffer, message_prefix, message_prefix_length);
    strncpy(buffer + message_prefix_length, userName, userName_size);
    buffer[message_prefix_length + userName_size] = '\0'; // Null-terminate the string
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
