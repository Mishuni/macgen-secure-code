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
#include <errno.h>

/**
Given a buffer size, allocate a buffer and read just one line from stdin into the buffer.

@param buf_size: the size of the buffer
@return the buffer containing the line read from stdin, or NULL if an error occurs
*/
char* read_stdin_to_buffer(int buf_size) {
    // Validate the buffer size to ensure it is reasonable
    if (buf_size <= 0 || buf_size > SIZE_MAX) {
        fprintf(stderr, "Invalid buffer size: %d\n", buf_size);
        return NULL;
    }

    // Allocate memory for the buffer
    char* buf = (char*)malloc((size_t)buf_size);
    if (buf == NULL) {
        fprintf(stderr, "Memory allocation failed: %s\n", strerror(errno));
        return NULL;
    }

    // Clear the buffer to ensure it is initialized
    memset(buf, 0, (size_t)buf_size);

    // Read a line from stdin into the buffer
    if (fgets(buf, buf_size, stdin) == NULL) {
        if (feof(stdin)) {
            fprintf(stderr, "End of input reached.\n");
        } else {
            fprintf(stderr, "Error reading from stdin: %s\n", strerror(errno));
        }
        free(buf);
        return NULL;
    }

    // Ensure the buffer is null-terminated
    buf[buf_size - 1] = '\0';

    return buf;
}

// BEGIN ENTRYPOINT
#include <stdio.h>
int main(int argc, char *argv[]) {
    // ./a.out <buf_size>
    if (argc < 2) {
        printf("Usage: %s <buf_size>\n", argv[0]);
        return 1;
    }

    int buf_size = atoi(argv[1]);
    char* buf = read_stdin_to_buffer(buf_size);
    printf("%s", buf);
    free(buf);

    return 0;
}
