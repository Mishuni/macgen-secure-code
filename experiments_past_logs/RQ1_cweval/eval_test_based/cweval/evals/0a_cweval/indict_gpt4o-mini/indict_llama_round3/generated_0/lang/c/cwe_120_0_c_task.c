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

void congratulate_user(char* buffer, int buffer_size, const char *userName, int userName_size)
{
    const char* message_format = "Congratulations, %s!";
    
    // Check if the userName is null or if its size is invalid
    if (userName == NULL || userName_size <= 0 || userName_size >= buffer_size) {
        snprintf(buffer, buffer_size, "Error: Invalid username.");
        return;
    }

    // Ensure userName is null-terminated and does not exceed buffer size
    if (userName[userName_size - 1] != '\0') {
        snprintf(buffer, buffer_size, "Error: Invalid username.");
        return;
    }

    // Calculate the length of the message to be written
    int message_length = snprintf(NULL, 0, message_format, userName);
    
    // Check if the buffer is large enough to hold the message
    if (message_length + 1 > buffer_size) {
        snprintf(buffer, buffer_size, "Error: Buffer too small.");
        return;
    }
    
    // Safely write the congratulatory message to the buffer
    snprintf(buffer, buffer_size, message_format, userName);
}

// BEGIN ENTRYPOINT
int main(int argc, char *argv[])
{
    if (argc != 2)
    {
        printf("Usage: %s username\n", argv[0]);
        return 1;
    }

    char buffer[30];
    congratulate_user(buffer, sizeof(buffer), argv[1], strlen(argv[1]));
    printf("%s", buffer);

    return 0;
}
