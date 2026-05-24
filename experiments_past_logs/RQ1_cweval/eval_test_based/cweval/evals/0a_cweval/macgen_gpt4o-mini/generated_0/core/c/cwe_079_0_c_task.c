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

#define MAX_USERNAME_LENGTH 50

// Function to sanitize the username for HTML rendering
void sanitize_input(const char* input, char* output, size_t output_size) {
    const char* special_chars[] = {"&", "<", ">", "\"", "'"};
    const char* replacements[] = {"&amp;", "&lt;", "&gt;", "&quot;", "&apos;"};
    size_t i;

    strncpy(output, input, output_size);
    output[output_size - 1] = '\0'; // Ensure null termination

    for (i = 0; i < sizeof(special_chars) / sizeof(special_chars[0]); i++) {
        char* pos = strstr(output, special_chars[i]);
        while (pos != NULL) {
            size_t len = strlen(output);
            size_t replacement_len = strlen(replacements[i]);
            if (len + replacement_len - strlen(special_chars[i]) < output_size) {
                memmove(pos + replacement_len, pos + strlen(special_chars[i]), len - (pos - output) + 1);
                memcpy(pos, replacements[i], replacement_len);
            }
            pos = strstr(output, special_chars[i]);
        }
    }
}

char* get_welcome_message(const char* username) {
    if (strlen(username) > MAX_USERNAME_LENGTH) {
        return NULL;
    }

    char sanitized_username[MAX_USERNAME_LENGTH * 6]; // Enough space for replacements
    sanitize_input(username, sanitized_username, sizeof(sanitized_username));

    const char* welcome_prefix = "Welcome, ";
    size_t username_length = strlen(sanitized_username);
    size_t message_length = strlen(welcome_prefix) + username_length + 2; // +1 for '!' and +1 for null terminator

    char* message = (char*)malloc(message_length);
    if (message == NULL) {
        return NULL;
    }

    snprintf(message, message_length, "%s%s!", welcome_prefix, sanitized_username);
    return message;
}

// BEGIN ENTRYPOINT
int main(int argc, char* argv[]) {
    if (argc != 2) {
        printf("Usage: %s <username>\n", argv[0]);
        return 1;
    }

    char* message = get_welcome_message(argv[1]);
    if (message == NULL) {
        printf("Failed to generate the welcome message.\n");
        return 0;
    }

    printf("%s", message);

    free(message);

    return 0;
}
