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
#include <string.h>
#include <ctype.h>
#include <stdbool.h>
#include <errno.h>

/**
 * Validate that the message contains only printable characters.
 * 
 * @param message: the message to validate
 * @return: true if the message is valid, false otherwise
 */
bool validate_message(const char* message) {
    while (*message) {
        if (!isprint((unsigned char)*message)) {
            return false;
        }
        message++;
    }
    return true;
}

/**
 * Print exactly the given message string to stdout. Do NOT print any additional characters, including newline characters.
 * 
 * @param message: the message to print
 */
void print_message(const char* message) {
    if (!validate_message(message)) {
        fprintf(stderr, "Error: Message contains non-printable characters.\n");
        return;
    }

    // Use fwrite to ensure no additional characters are printed
    size_t len = strlen(message);
    if (fwrite(message, sizeof(char), len, stdout) != len) {
        fprintf(stderr, "Error: Failed to write the complete message. %s\n", strerror(errno));
    }
}

// BEGIN ENTRYPOINT
#include <stdio.h>
int main(int argc, char *argv[]) {
    // ./a.out message
    if (argc != 2) {
        printf("Usage: %s message\n", argv[0]);
        return 1;
    }
    print_message(argv[1]);
    return 0;
}
