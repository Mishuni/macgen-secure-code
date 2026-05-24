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
    int required_length = strlen(prefix) + userName_size + strlen(suffix) + 1; // +1 for null terminator

    if (buffer_size >= required_length) {
        snprintf(buffer, buffer_size, "%s%s%s", prefix, userName, suffix);
    } else if (buffer_size > 0) {
        int available_space = buffer_size - 1; // Reserve space for null terminator
        snprintf(buffer, buffer_size, "%.*s%.*s%.*s", 
                 available_space > strlen(prefix) ? (int)strlen(prefix) : available_space, prefix,
                 available_space > strlen(prefix) ? available_space - (int)strlen(prefix) : 0, userName,
                 available_space > strlen(prefix) + userName_size ? available_space - (int)strlen(prefix) - userName_size : 0, suffix);
        buffer[buffer_size - 1] = '\0'; // Ensure null termination
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
