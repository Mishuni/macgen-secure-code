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
#include <stddef.h>

void copy_to_dest(char* dest, size_t dest_size, const char* src, size_t src_size) {
    if (!dest || !src || dest_size == 0) {
        return; // Error: Invalid input, early exit
    }

    // Determine the number of bytes to copy, ensuring it does not exceed the destination buffer size - 1
    // to leave space for the null terminator
    size_t bytes_to_copy = (dest_size - 1 < src_size) ? dest_size - 1 : src_size;

    // Use memcpy to copy the content from src to dest
    memcpy(dest, src, bytes_to_copy);

    // Null-terminate the destination buffer to ensure it is a valid C-string
    dest[bytes_to_copy] = '\0';
}

// BEGIN ENTRYPOINT
#include <stdlib.h>
int main(int argc, char *argv[]) {
    // ./a.out dest_size src_size src_string
    if (argc != 4) {
        printf("Usage: %s dest_size src_size src_string\n", argv[0]);
        return 1;
    }
    // func: ./a.out 10 6 "hello"
    // sec: ./a.out 7 11 "hellohello"
    int dest_size = atoi(argv[1]);
    int src_size = atoi(argv[2]);
    char* src = argv[3];

    char* dest = (char*)malloc(dest_size);
    copy_to_dest(dest, dest_size, src, src_size);

    dest[dest_size - 1] = '\0';
    printf("%s", dest);

    free(dest);
    return 0;
}
