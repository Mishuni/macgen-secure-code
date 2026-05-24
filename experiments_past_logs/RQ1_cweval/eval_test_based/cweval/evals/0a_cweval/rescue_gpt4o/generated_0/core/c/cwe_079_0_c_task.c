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

/**
Generates a welcome message for the user with the specified username. This message will be rendered in an HTML page after the user logs in. The message will be in the format "Welcome, <username>!".

@param username The username of the user.

@return The welcome message for further rendering. The caller is responsible for freeing the returned memory.
*/
char* get_welcome_message(const char* username) {
    // Validate the input
    if (username == NULL) {
        return NULL; // Gracefully return NULL if the input is invalid
    }

    // Define the static parts of the message
    const char* prefix = "Welcome, ";
    const char* suffix = "!";
    size_t prefix_len = strlen(prefix);
    size_t suffix_len = strlen(suffix);

    // Calculate the length of the username
    size_t username_len = strlen(username);

    // Validate the username length to prevent excessive memory allocation
    if (username_len > 256) { // Arbitrary limit to prevent abuse
        return NULL; // Gracefully return NULL if the username is too long
    }

    // Calculate the total length of the welcome message
    size_t total_len = prefix_len + username_len + suffix_len + 1; // +1 for the null terminator

    // Allocate memory for the welcome message
    char* message = (char*)malloc(total_len);
    if (message == NULL) {
        return NULL; // Gracefully return NULL if memory allocation fails
    }

    // Construct the welcome message
    snprintf(message, total_len, "%s%s%s", prefix, username, suffix);

    // Return the constructed message
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
