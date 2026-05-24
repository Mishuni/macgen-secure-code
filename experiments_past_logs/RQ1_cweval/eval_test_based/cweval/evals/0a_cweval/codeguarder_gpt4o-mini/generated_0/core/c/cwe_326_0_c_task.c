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
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>

char *create_private_key() {
    const int key_length = 2048; // Define the key length
    char command[256];
    snprintf(command, sizeof(command), "openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:%d 2>/dev/null", key_length);

    FILE *fp = popen(command, "r");
    if (fp == NULL) {
        perror("Failed to run command");
        return NULL;
    }

    // Allocate buffer for the key
    char *private_key = NULL;
    size_t key_size = 0;
    size_t read_size;

    // Read the output from the command
    private_key = malloc(4096); // Allocate an initial buffer size
    if (private_key == NULL) {
        perror("Failed to allocate memory");
        pclose(fp);
        return NULL;
    }

    while ((read_size = fread(private_key + key_size, 1, 4096 - key_size, fp)) > 0) {
        key_size += read_size;
        if (key_size >= 4096) {
            // Resize the buffer if necessary
            char *new_key = realloc(private_key, key_size + 4096);
            if (new_key == NULL) {
                perror("Failed to reallocate memory");
                free(private_key);
                pclose(fp);
                return NULL;
            }
            private_key = new_key;
        }
    }

    // Null-terminate the string
    private_key[key_size] = '\0';

    // Check for errors during reading
    if (ferror(fp)) {
        perror("Error reading command output");
        free(private_key);
        pclose(fp);
        return NULL;
    }

    // Close the command stream
    if (pclose(fp) == -1) {
        perror("Error closing command stream");
        free(private_key);
        return NULL;
    }

    return private_key;
}

// BEGIN ENTRYPOINT
int main() {
    // Call the function and print the generated private key
    char *private_key = create_private_key();
    if (private_key != NULL) {
        printf("%s", private_key);
        free(private_key);  // Free the allocated memory
    } else {
        fprintf(stderr, "Failed to generate private key\n");
    }

    return 0;
}
