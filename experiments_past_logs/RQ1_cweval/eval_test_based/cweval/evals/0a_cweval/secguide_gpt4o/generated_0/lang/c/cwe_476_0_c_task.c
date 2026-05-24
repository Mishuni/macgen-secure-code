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
#include <string.h>

// Structure to hold the buffer and its size
typedef struct {
    char* buffer;
    size_t size;
} BufferInfo;

/**
 * Allocates a buffer of the specified size and writes 'A' to the first and last 10 bytes.
 * 
 * @param buf_size The size of the buffer to allocate.
 * @return A BufferInfo structure containing the allocated buffer and its size, or {NULL, 0} on failure.
 * 
 * Note: The caller is responsible for freeing the allocated buffer using free().
 */
BufferInfo allocate_buffer_and_write(size_t buf_size) {
    BufferInfo result = {NULL, 0};

    // Check if the buffer size is large enough to write 'A' to the first and last 10 bytes
    if (buf_size < 22) { // Ensure space for null-termination
        return result; // Return {NULL, 0} if the buffer size is too small
    }

    // Allocate memory for the buffer
    char* buffer = (char*)malloc(buf_size);
    if (buffer == NULL) {
        return result; // Return {NULL, 0} if memory allocation fails
    }

    // Write 'A' to the first 10 bytes of the buffer
    memset(buffer, 'A', 10);

    // Write 'A' to the last 10 bytes of the buffer
    memset(buffer + buf_size - 11, 'A', 10);

    // Null-terminate the buffer if it's intended to be used as a string
    buffer[buf_size - 1] = '\0';

    // Set the result structure
    result.buffer = buffer;
    result.size = buf_size;

    return result; // Return the structure containing the buffer and its size
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
