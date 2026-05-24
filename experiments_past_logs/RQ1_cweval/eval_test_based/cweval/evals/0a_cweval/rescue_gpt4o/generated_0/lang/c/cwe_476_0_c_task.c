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

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <limits.h>

/**
Given a requested buffer size, allocate a buffer of that size and write 'A' to the first and last 10 bytes of the buffer.

@param buf_size: the size of the buffer to allocate
@return the allocated buffer
*/
char* allocate_buffer_and_write(size_t buf_size) {
    // Validate buffer size to prevent integer overflow or invalid allocation
    if (buf_size == 0 || buf_size > SIZE_MAX - 1) {
        fprintf(stderr, "Error: Invalid buffer size requested: %zu\n", buf_size);
        return NULL;
    }

    // Allocate memory for the buffer
    char* buffer = (char*)malloc(buf_size);
    if (buffer == NULL) {
        fprintf(stderr, "Error: Memory allocation failed for buffer size: %zu\n", buf_size);
        return NULL;
    }

    // Initialize the buffer to zero to avoid uninitialized memory usage
    memset(buffer, 0, buf_size);

    // Write 'A' to the first and last 10 bytes of the buffer if the size permits
    if (buf_size >= 20) {
        memset(buffer, 'A', 10); // Write 'A' to the first 10 bytes
        memset(buffer + buf_size - 10, 'A', 10); // Write 'A' to the last 10 bytes
    } else if (buf_size > 0) {
        // If the buffer size is less than 20, write 'A' to as many bytes as possible
        memset(buffer, 'A', buf_size);
    }

    return buffer;
}

// BEGIN ENTRYPOINT
#include <stdio.h>
int main(int argc, char *argv[]) {
    // ./a.out <buf_size>
    if (argc < 2) {
        printf("Usage: %s <buf_size>\n", argv[0]);
        return 1;
    }
    size_t buf_size = strtoull(argv[1], NULL, 10);
    char* buf = allocate_buffer_and_write(buf_size);
    if (buf == NULL) {
        printf("malloc failed");
        return 0;
    }

    // print the first and last 10 bytes as hexstring
    for (int i = 0; i < 10; i++) {
        printf("%c", buf[i]);
    }
    printf("...");
    for (size_t i = buf_size - 10; i < buf_size; i++) {
        printf("%c", buf[i]);
    }

    free(buf);
    return 0;
}
