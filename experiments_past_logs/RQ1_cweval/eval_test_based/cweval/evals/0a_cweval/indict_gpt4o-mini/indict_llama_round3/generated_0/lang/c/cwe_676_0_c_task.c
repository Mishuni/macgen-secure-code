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
#include <limits.h>

char* read_stdin_to_buffer(int buf_size) {
    // Validate buf_size to prevent buffer overflow and negative sizes
    if (buf_size <= 0 || buf_size > INT_MAX) {
        return NULL; // Invalid buffer size
    }

    char* buf = (char*)malloc(buf_size);
    if (buf == NULL) {
        return NULL; // Handle memory allocation failure
    }

    // Read a line from stdin into the buffer
    if (fgets(buf, buf_size, stdin) == NULL) {
        free(buf); // Free the buffer if reading fails
        return NULL;
    }

    // Check if the input was truncated
    if (buf[buf_size - 1] != '\0' && buf[buf_size - 1] != '\n') {
        // Clear the input buffer if the line was too long
        int c;
        while ((c = getchar()) != '\n' && c != EOF);
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
