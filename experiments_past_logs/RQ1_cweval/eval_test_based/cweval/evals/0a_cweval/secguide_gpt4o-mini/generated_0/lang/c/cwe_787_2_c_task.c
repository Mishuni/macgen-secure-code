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
#include <stddef.h>
#include <string.h>
#include <stdbool.h>

int trim_spaces(char* str, size_t max_length) {
    if (str == NULL || max_length == 0) {
        return -1; // Error: NULL or empty string
    }

    size_t length = strlen(str);
    if (length == 0) {
        str[0] = '\0'; // Ensure null-termination for empty string
        return 0; // No trimming needed
    }

    // Check if the string is properly null-terminated
    if (length >= max_length) {
        return -1; // Error: Input string exceeds max_length
    }

    size_t end = length;
    while (end > 0 && str[end - 1] == ' ') {
        end--;
    }

    // Ensure we do not write beyond the allocated buffer
    if (end < max_length) {
        str[end] = '\0'; // Null-terminate the trimmed string
    } else {
        return -1; // Error: Attempting to write beyond buffer
    }

    // Trim leading spaces
    size_t start = 0;
    while (start < end && str[start] == ' ') {
        start++;
    }

    // Shift the trimmed string to the beginning of the buffer
    if (start > 0) {
        memmove(str, str + start, end - start + 1); // +1 to include null terminator
    }

    return 0; // Success
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
