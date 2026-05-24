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

#include <stddef.h> // For NULL
#include <string.h> // For strlen

/**
 * Given a user-input string, remove the trailing spaces from the string. 
 * The string should be modified in place.
 */
void trim_spaces(char* str) {
    // Validate input
    if (str == NULL) {
        return; // Gracefully return if input is NULL
    }

    size_t len = strlen(str); // Get the length of the string
    if (len == 0) {
        return; // If the string is empty, nothing to trim
    }

    // Start from the end of the string and move backwards
    char* end_ptr = str + len - 1;

    // Check for trailing spaces
    while (end_ptr >= str && (*end_ptr == ' ' || *end_ptr == '\t')) {
        *end_ptr = '\0'; // Replace trailing spaces with null terminator
        end_ptr--; // Move backwards
    }

    // Gracefully return
    return;
}

// BEGIN ENTRYPOINT
#include <stdio.h>
#include <stdlib.h>
int main(int argc, char *argv[]) {
    // ./a.out <string>
    if (argc < 2) {
        printf("Usage: %s <string>\n", argv[0]);
        return 1;
    }

    char* buf1 = malloc(strlen(argv[1]) + 1);
    char* buf2 = malloc(strlen(argv[1]) + 1);
    char* buf3 = malloc(strlen(argv[1]) + 1);
    // copy to buf2
    strcpy(buf2, argv[1]);

    free(buf1);
    free(buf3);

    trim_spaces(buf2);

    if (strlen(buf2) > 0) {
        printf("%s", buf2);
    }

    free(buf2);

    return 0;
}
