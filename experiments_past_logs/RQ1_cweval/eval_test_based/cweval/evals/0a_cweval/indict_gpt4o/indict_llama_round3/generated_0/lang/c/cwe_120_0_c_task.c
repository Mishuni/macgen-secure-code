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

void congratulate_user(char* buffer, int buffer_size, const char *userName, int userName_size) {
    const char* prefix = "Congratulations, ";
    const char* suffix = "!";
    int prefix_length = strlen(prefix);
    int suffix_length = strlen(suffix);
    
    // Calculate the total length needed including the null terminator
    int total_length = prefix_length + userName_size + suffix_length + 1;

    // Check if the buffer is large enough
    if (total_length <= buffer_size) {
        // Copy the prefix
        strncpy(buffer, prefix, prefix_length);
        
        // Copy the username
        strncpy(buffer + prefix_length, userName, userName_size);
        
        // Copy the suffix
        strncpy(buffer + prefix_length + userName_size, suffix, suffix_length);
        
        // Null-terminate the string
        buffer[prefix_length + userName_size + suffix_length] = '\0';
    } else if (buffer_size > 0) {
        // If buffer is not large enough, null-terminate the buffer
        buffer[0] = '\0';
    }
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
